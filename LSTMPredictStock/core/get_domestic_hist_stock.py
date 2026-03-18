import json
import os
import requests
import yfinance as yf
from datetime import datetime,timedelta
import csv
def get_twse_stock(stock_code, start_date, end_date): #本來有寫開始日期跟結束的，但是改成yfinance後就沒用了，而且function就沒刪去
    """
    從 Yahoo Finance 抓取台股數據，並儲存為 CSV 檔案。
    """
    stock_id = f"{stock_code}.TW"
    ticker = yf.Ticker(stock_id)
    data = ticker.history(period="10y")
    data["Stock_Code"] = stock_code #寫入股票代碼(說不定會用到)
    data = data.reset_index()
    data["Date"] = data["Date"].dt.strftime("%Y-%m-%d")
    root = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(root,"config.json") #寫入公司名稱(說不定會用到)
    with open(config_path, "r", encoding="utf-8") as config_file:
        configs = json.load(config_file)
    companies_name = configs['companies'][stock_code]
    data["Name"] = companies_name 


    file_path = os.path.join(root+"/data", f"{stock_code}.csv")
    print(file_path)
    data.to_csv(file_path, index=False)

def get_all_last_data(start_date="2015-01-01"):
    root = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(root,"config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        configs = json.load(f)
    companies = configs['companies']

    cur = datetime.now()
    year = timedelta(days=365)
    cur = cur + year    
    end_date = cur.strftime("%Y-%m-%d")  

    for code, company_name in companies.items():
        get_twse_stock(code, start_date, end_date)

def get_single_last_data(stock_code,start_date="2015-01-01"):
    cur = datetime.now()
    year = timedelta(days=365)
    cur = cur + year 
    end_date = cur.strftime("%Y-%m-%d") 

    get_twse_stock(stock_code, start_date, end_date)


if __name__ == '__main__':
    get_all_last_data("2015-01-01")
