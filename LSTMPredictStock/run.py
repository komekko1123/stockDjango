import keras

__author__ = "Jakob Aungiers"
__copyright__ = "Jakob Aungiers 2018"
__version__ = "2.0.0"
__license__ = "MIT"

import os
import json
import numpy as np
import math
import pandas as pd
from LSTMPredictStock.core.data_processor import DataLoader
from LSTMPredictStock.core.model import Model
from datetime import datetime,timedelta
from LSTMPredictStock.core.get_domestic_hist_stock import get_all_last_data
from LSTMPredictStock.core.get_domestic_hist_stock import get_single_last_data






def train_model(stock_code): 
    configs = json.load(open(get_config_path(), 'r', encoding="utf-8"))
    if not os.path.exists(os.path.join(get_parent_dir(),configs['model']['save_dir'])):
        os.makedirs(os.path.join(get_parent_dir(),configs['model']['save_dir'])) 

    split = configs['data']['train_test_split']

    data = DataLoader(  
        os.path.join(get_parent_dir(),os.path.join('data', stock_code + ".csv")),  
        split,
        configs['data']['columns']  
    )

    model = Model()
    model.build_model(configs) 

    x_train, y_train = data.get_train_data(seq_len=configs['data']['sequence_length'], normalise=configs['data']['normalise'])
    # in-memory training
    model.train(
        x=x_train,
        y=y_train,
        epochs = configs['training']['epochs'],
        batch_size = configs['training']['batch_size'],
        save_dir = os.path.join(get_parent_dir(),configs['model']['save_dir']),
        save_name = stock_code
    )

def prediction(stock_code, no_real=True, pre_len=30): #for prediction
    config_path = get_config_path()
    configs = json.load(open(config_path, 'r', encoding="utf-8"))
    data = DataLoader(
        os.path.join(get_data_path(), stock_code + ".csv"),  
        configs['data']['train_test_split'],
        configs['data']['columns']
    )
    
    file_path = os.path.join(get_parent_dir(),os.path.join("saved_models",stock_code + ".h5"))
    if not os.path.exists(file_path):
        print(f"model不存在，開始訓練model: {file_path}")
        train_model(stock_code) #不存在就生然後train
    else:
        print(f"find model: {file_path}")

    model = Model()
    keras.backend.clear_session()
    model.load_model(file_path)  # for config to create model


    predict_length = pre_len
    if no_real:  
        win_position = -1
    else:  
        win_position = -configs['data']['sequence_length']

    x_test, y_test = data.get_test_data(
        seq_len=configs['data']['sequence_length'],
        normalise=False
    )

    x_test = x_test[win_position]
    x_test = x_test[np.newaxis, :, :]
    if not no_real:
        y_test_real = y_test[win_position:win_position + predict_length]

    base = x_test[0][0][0]
    print("base value:\n", base)

    x_test, y_test = data.get_test_data(
        seq_len=configs['data']['sequence_length'],
        normalise=configs['data']['normalise']
    )

    predictions = model.predict_sequences_multiple(x_test, configs['data']['sequence_length'], predict_length)
    x_test = x_test[win_position]
    x_test = x_test[np.newaxis, :, :]


    predictions = model.predict_1_win_sequence(x_test, configs['data']['sequence_length'], predict_length) # normalization
    predictions_array = np.array(predictions)
    predictions_array = base * (1 + predictions_array)
    predictions = predictions_array.tolist()

    print("Predict data:\n", predictions)
    if not no_real:
        print("Real data：\n", y_test_real)

    return format_predictions(predictions)

def format_predictions(predictions):
    # 給預測數據添加對應日期
    date_predict = []
    now = datetime.now()
    # 確定是否已過關盤時間 (假設關盤時間為當日下午 2 點)
    market_close_time = now.replace(hour=14, minute=0, second=0, microsecond=0)
    # 如果當前時間小於關盤時間，從今天開始預測；否則從明天開始預測
    if now < market_close_time:
        cur = now
    else:
        cur = now + timedelta(days=1)
    counter = 0
    while counter < len(predictions):
        # 跳過週末
        if cur.isoweekday() == 6:  # 星期六
            cur = cur + timedelta(days=2)
        elif cur.isoweekday() == 7:  # 星期日
            cur = cur + timedelta(days=1)
        # 添加預測日期和對應的值
        date_predict.append([cur.strftime("%Y-%m-%d"), predictions[counter]])
        # 前進一天
        cur = cur + timedelta(days=1)
        counter += 1
    return date_predict


def get_hist_data(stock_code, recent_day=30): 
    get_single_last_data(stock_code)
    root_dir = get_parent_dir()
    file_path = os.path.join(root_dir, "data/" + stock_code + ".csv")
    cols = ['Date', 'Close']
    data_frame = pd.read_csv(file_path)
    close_data = data_frame.get(cols).values[-recent_day:]
    return close_data.tolist()


def train_all_stock():  #
    get_all_last_data(start_date="2015-01-01")
    configs = json.load(open(get_config_path(), 'r', encoding="utf-8"))
    companies = configs['companies']
    print("正在train")
    for stock_code in companies.keys():
        train_model(stock_code)

    return 0


def predict_all_stock(pre_len=10):
    file_path = get_config_path()
    configs = json.load(open(file_path, 'r',encoding="utf-8"))
    companies = configs['companies']
    predict_list = []
    for stock_code in companies.keys():
        predict_list.append(prediction(stock_code=stock_code, no_real=True, pre_len=pre_len))

    return predict_list


def get_config_path():  
    root_dir = get_parent_dir()
    return os.path.join(root_dir, "config.json")


def get_data_path(): 
    root_dir = get_parent_dir()
    return os.path.join(root_dir, "data")


def get_parent_dir():   
    return os.path.dirname(__file__)


if __name__ == '__main__':
    train_all_stock()
    predict_all_stock()
    #開始train

