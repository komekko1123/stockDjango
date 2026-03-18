import pandas as pd
import numpy as np
import os
import ta
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime,timedelta
from math import pi
import json
#plt.style.use('seaborn')

parent_dir = os.path.dirname(__file__)
json_path = os.path.join(parent_dir, "companies_name_code.json")
print(json_path)


def printUnivList(stock_code, num):
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            stock_names = json.load(file)
    except FileNotFoundError:
        print(f"Error: 找不到文件 {json_path}")
        stock_names = {}
    
    stock_id = f"{stock_code}.TW"
    ticker = yf.Ticker(stock_id)
    data = ticker.history(period="10y")
    data = data.reset_index()
    name = stock_names.get(stock_code, "未知股票")
    print(name)


    ####################################################
    data["Date"] = data["Date"].dt.strftime("%Y-%m-%d")
    #  長期趨勢 用(移動平均線看黃金交叉的東西，ppt上有)
    data['SMA50'] = ta.trend.SMAIndicator(close=data['Close'], window=50).sma_indicator()
    data['SMA200'] = ta.trend.SMAIndicator(close=data['Close'], window=200).sma_indicator()
    #  強度 - RSI 和 MACD 用(RSI 70=賣 RSI 30=買，ppt上有)
    data['RSI'] = ta.momentum.RSIIndicator(close=data['Close'], window=14).rsi()
    macd = ta.trend.MACD(close=data['Close'], window_slow=26, window_fast=12, window_sign=9)
    data['MACD'] = macd.macd()
    data['MACD_Signal'] = macd.macd_signal()

    #  資金 - OBV 和 CMF(這是知識盲區了)
    data['OBV'] = ta.volume.OnBalanceVolumeIndicator(close=data['Close'], volume=data['Volume']).on_balance_volume()
    data['CMF'] = ta.volume.ChaikinMoneyFlowIndicator(high=data['High'], low=data['Low'], close=data['Close'], volume=data['Volume'], window=20).chaikin_money_flow()

    # 短期預期 - ROC 和 隨機指標（Stochastic Oscillator）(這是知識盲區了)
    data['ROC'] = ta.momentum.ROCIndicator(close=data['Close'], window=12).roc()
    stoch = ta.momentum.StochasticOscillator(high=data['High'], low=data['Low'], close=data['Close'], window=14, smooth_window=3)
    data['Stoch'] = stoch.stoch()

    # 風險 - ATR 和 布林度寬帶(這是知識盲區了，太股市了)
    data['ATR'] = ta.volatility.AverageTrueRange(high=data['High'], low=data['Low'], close=data['Close'], window=14).average_true_range()
    bollinger = ta.volatility.BollingerBands(close=data['Close'], window=20, window_dev=2)
    data['Bollinger_Width'] = bollinger.bollinger_wband()
    data.dropna(inplace=True)
    #******************************************

    # 正則化 map到0~10範圍
    def normalize(series, reverse=False):
        min_val = series.min()
        max_val = series.max()
        if max_val - min_val == 0:
            return np.zeros_like(series)
        normalized = (series - min_val) / (max_val - min_val) * 10
        if reverse:
            normalized = 10 - normalized
        return normalized

    # 長期趨勢評分
    data['Score_Trend'] = normalize(data['SMA50'] - data['SMA200'])

    # 強度評分
    data['Score_Strength'] = (normalize(data['RSI']) + normalize(data['MACD'] - data['MACD_Signal'])) / 2

    # 資金評分
    data['Score_Funds'] = (normalize(data['OBV']) + normalize(data['CMF'])) / 2

    # 短期預期評分
    data['Score_Expectation'] = (normalize(data['ROC']) + normalize(data['Stoch'])) / 2

    # 風險評分
    data['Score_Risk'] = (normalize(data['ATR'], reverse=True) + normalize(data['Bollinger_Width'], reverse=True)) / 2
    
    weights = {
        'Score_Trend': 0.2,
        'Score_Strength': 0.2,
        'Score_Funds': 0.15,
        'Score_Expectation': 0.15,
        'Score_Risk': 0.1
    }

    # 綜合评分
    data['Score_Comprehensive'] = sum(weights[key] * data[key] for key in weights.keys())

    #強烈推薦購買：綜合評分 > 7。
    #推薦購買：6 <= 綜合評分 <= 7。
    #觀望：4 <= 綜合評分 < 6。
    #建議賣出：綜合評分 < 4。

    indicator_columns = ['Date','Score_Trend', 'Score_Comprehensive', 'Score_Strength', 'Score_Funds', 'Score_Expectation', 'Score_Risk']
    missing_columns = [col for col in indicator_columns if col not in data.columns]
    indicators_df = data[indicator_columns].tail(num).copy()



    # 選擇五天日期進行繪製，例如最新的一天
    #趨勢 (Score_Time)：用於長期趨勢判斷。
    #強度 (Score_Strength)：用於動能評估。
    #資金 (Score_Funds)：反映市場資金流向。
    #預期 (Score_Expectation)：短期市場走勢的預測。
    #風險 (Score_Risk)：評估波動性和潛在風險。
    latest_date = data.index[-1]
    days = data['Date'].tail(1).values[0]
    print(days)
    indicators_df['Stock_code'] = stock_code #放入code
    indicators_df['Name'] = name             #放入名字
    # categories = ['趨勢', '強度', '資金', '預期', '風險']
    # 获取对应评分
    # values = indicators_df.loc[latest_date, ['Score_Trend', 'Score_Strength', 'Score_Funds', 
    #                                 'Score_Expectation',  'Score_Risk']].values.tolist()

    # # 添加第一个值到末尾以闭合雷达图
    # values += values[:1]
    # num_vars = len(categories)

    # # 计算角度
    # angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
    # angles += angles[:1]

    # # 绘制雷达图
    # plt.figure(figsize=(8, 8))
    # ax = plt.subplot(111, polar=True)

    # # 绘制类别
    # plt.xticks(angles[:-1], categories, color='grey', size=8)

    # # 绘制y轴
    # ax.set_rlabel_position(30)
    # plt.yticks([2,4,6,8], ["2","4","6","8"], color="grey", size=7)
    # plt.ylim(0,10)

    # # 绘制数据
    # ax.plot(angles, values, linewidth=1, linestyle='solid', label='评分')
    # ax.fill(angles, values, 'skyblue', alpha=0.4)

    # plt.title(f'{stock_id} TSMC ({days})', size=15, y=1.1)
    # plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    # plt.show()


    ####################################################
    shares = []
    parent_dir = os.path.dirname(__file__)  
    file_dir = os.path.join(parent_dir,"stock_index/")
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    file_path = os.path.join(file_dir,stock_code+'.csv')
    indicators_df.to_csv(file_path, index=False)

def main(stock_code):
  printUnivList(stock_code, 10)  

def update_csv():
  try:
    with open(json_path, "r", encoding="utf-8") as file:
        stock_names = json.load(file)
  except FileNotFoundError:
        print(f"Error: 找不到文件 {json_path}")
        stock_names = {}
  for stock_code in stock_names.keys():
    main(stock_code)
# =============================================================================
# def main():
#     uinfo = []
#     url = 'http://www.gpdatacat.com/index.php?r=stock%2Fview&stockcode=000063'
#     html = getHTMLText(url)
#     fillUnivList(uinfo, html)
#     printUnivList(uinfo, 10)  #50个日期
# main()
# "2330": "台積電",
#	"2498": "宏達電",
#	"2609": "陽明",
#	"5471": "松翰",
#	"3694": "海華"
# =============================================================================



