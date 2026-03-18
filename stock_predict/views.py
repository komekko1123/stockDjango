import json
import os
from django.http import FileResponse
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from LSTMPredictStock import run
from LSTMPredictStock.core.get_domestic_hist_stock import get_single_last_data
from .get_stock_index import printUnivList,update_csv
from stock_predict import models
from datetime import datetime as dt
from apscheduler.scheduler import Scheduler
from .models import Company
from .models import StockIndex
from datetime import datetime,timedelta
import pandas as pd
from django.views.decorators.csrf import csrf_exempt

LOCAL = True
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # D:\WebStockPredict-master
CONFIG_PATH = os.path.join(BASE_DIR, "LSTMPredictStock", "config.json")  # D:\WebStockPredict-master\LSTMPredictStock\config.json
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # D:\WebStockPredict-master\stock_predict
COMPANIES_PATH = os.path.join(CURRENT_DIR, "companies_name_code.json")  # D:\WebStockPredict-master\stock_predict\companies_name_code.json




@csrf_exempt
def delete_companies(request):
    if request.method == "GET":
        try:
            with open(COMPANIES_PATH, "r", encoding="utf-8") as file:
                companies = json.load(file)
        except FileNotFoundError:
            companies = {}
        return render(request, "stock_predict/delete_companies.html", {"companies": companies})

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            stock_code = data.get("stock_code")

            if not stock_code:
                return JsonResponse({"error": "未提供公司代碼"}, status=400)

            # 刪除相關數據和模型
            company = get_object_or_404(Company, stock_code=stock_code)
            company.predictdata_set.all().delete()
            company.historydata_set.all().delete()
            company.stockindex_set.all().delete()
            company.delete()

            # 刪除 CSV 文件
            file_dir = os.path.join(CURRENT_DIR, "stock_index")
            file_path = os.path.join(file_dir, f"{stock_code}.csv")

            LSTM_file_dir = os.path.join(BASE_DIR, "LSTMPredictStock")

            LSTM_csvdata_dir = os.path.join(LSTM_file_dir, "data")
            LSTM_csvdata_path = os.path.join(LSTM_csvdata_dir, f"{stock_code}.csv")
            LSTM_modeldata_dir = os.path.join(LSTM_file_dir, "saved_models")
            LSTM_modeldata_path = os.path.join(LSTM_modeldata_dir, f"{stock_code}.h5")

            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(LSTM_csvdata_path):
                os.remove(LSTM_csvdata_path)
            if os.path.exists(LSTM_modeldata_path):
                os.remove(LSTM_modeldata_path)

            # 更新 JSON 文件
            with open(COMPANIES_PATH, "r", encoding="utf-8") as file:
                companies = json.load(file)
            companies.pop(stock_code, None)
            with open(COMPANIES_PATH, "w", encoding="utf-8") as file:
                json.dump(companies, file, ensure_ascii=False, indent=4)

            with open(CONFIG_PATH, "r", encoding="utf-8") as file:
                config = json.load(file)
            config["companies"].pop(stock_code, None)
            with open(CONFIG_PATH, "w", encoding="utf-8") as file:
                json.dump(config, file, ensure_ascii=False, indent=4)

            return JsonResponse({"success": True, "deleted_company": stock_code}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "僅支持 GET 和 POST 請求"}, status=405)


def get_hist_predict_data(stock_code):#查看您提供的 Django 視圖函數，recent_data 和 predict_data 是通過 get_hist_predict_data 方法獲取的：
    recent_data,predict_data = None,None
    company = get_object_or_404(Company, stock_code=stock_code)

    if company.historydata_set.count() <= 0:
        history_data = models.HistoryData()
        history_data.company = company
        history_data.set_data(run.get_hist_data(stock_code=stock_code,recent_day=20))
        history_data.save()
        recent_data = history_data.get_data()
    else:
        all_data = company.historydata_set.all()
        for single in all_data:
            now = dt.now()
            end_date = single.get_data()[-1][0]
            end_date = dt.strptime(end_date,"%Y-%m-%d")
            if LOCAL & (now.date() > end_date.date()):        # 更新预测数据
                single.set_data(run.get_hist_data(stock_code=stock_code,recent_day=20))
                single.save()
               
            recent_data = single.get_data()
            break

    if company.predictdata_set.count() <= 0:
        predict_data = models.PredictData()
        predict_data.company = company
        predict_data.set_data(run.prediction(stock_code,pre_len=10))
        predict_data.save()
        predict_data = predict_data.get_data()
    else:
        all_data = company.predictdata_set.all()
        for single in all_data:
            now = dt.now()
            start_date = dt.strptime(single.start_date,"%Y-%m-%d")
            if LOCAL & (now.date() > start_date.date()):  # 更新预测数据
                single.set_data(run.prediction(stock_code, pre_len=10))
                single.save()
            predict_data = single.get_data()
            break
    return recent_data,predict_data

def get_crawl_save_data():
    # Date Score_Strength Score_Trend Score_Funds Score_Expectation Score_Risk
    parent_dir = os.path.dirname(__file__)  # "stock_predict/views.py"
    file_dir = os.path.join(parent_dir, "stock_index/")
    with open(COMPANIES_PATH, "r", encoding="utf-8") as file:
      companies_name_code = json.load(file)

   # print(company.stockindex_set.count(),"進到function拿資料")
    for file_name in os.listdir(file_dir):
        file_path =  os.path.join(file_dir, file_name)
        data_frame = pd.read_csv(file_path)
        stock_code = file_name.split('.')[0]


        if not Company.objects.filter(stock_code=stock_code).exists(): # 如果不存在，新增公司 ，應該不會有問題 ，因為這裡是找stock_index的csv檔
            Company.objects.create(stock_code=stock_code, name=companies_name_code[stock_code])
            print(f"新增公司: {companies_name_code[stock_code]} (股票代碼: {stock_code})")


        company = get_object_or_404(Company, stock_code=stock_code)
        for index,row in data_frame.iterrows():
            date_str = row['Date']
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print(f"日期格式错误: {date_str}")
                continue  

            stock_index, created = StockIndex.objects.get_or_create(
                company=company,
                Date=date_obj,
                defaults={
                    'Score_Strength': row['Score_Strength'],
                    'Score_Trend': row['Score_Trend'],
                    'Score_Funds': row['Score_Funds'],
                    'Score_Expectation': row['Score_Expectation'],
                    'Score_Risk': row['Score_Risk'],
                    'Score_Comprehensive': row['Score_Comprehensive']
                }
            )
            if not created:
                # 如果紀錄已存在，则更新字段
                stock_index.Score_Strength = row['Score_Strength']
                stock_index.Score_Trend = row['Score_Trend']
                stock_index.Score_Funds = row['Score_Funds']
                stock_index.Score_Expectation = row['Score_Expectation']
                stock_index.Score_Risk = row['Score_Risk']
                stock_index.Score_Comprehensive = row['Score_Comprehensive']
                stock_index.save()
                print(f"更新紀錄: {company.stock_code} - {date_obj}")
            else:
                print(f"創建新紀錄: {company.stock_code} - {date_obj}")
        
        # 删除舊紀錄，保留最新N天的数据(gpt)
        cutoff_date = datetime.today().date() - timedelta(days=7)
        old_records = company.stockindex_set.filter(Date__lt=cutoff_date)
        deleted_count, _ = old_records.delete()
        print(f"删除 {deleted_count} 條 {stock_code} 的舊紀錄 (日期 < {cutoff_date})")
            
# 確保 CSRF 驗證對於此 API 關閉
@csrf_exempt
def update_companies(request):
    if request.method == "GET":
        # 如果是 GET 請求，返回更新頁面
        return render(request, "stock_predict/update_companies.html")
    
    if request.method == "POST":
        try:
            # 獲取前端傳來的數據
            data = json.loads(request.body)
            code = data.get("code")
            name = data.get("name")
            if not code or not name:
                return JsonResponse({"error": "公司代碼或名稱缺失"}, status=400)


            # 讀取 config.json
            with open(CONFIG_PATH, "r", encoding="utf-8") as file:
                config = json.load(file)
            # 更新 companies 部分
            if "companies" not in config:
                config["companies"] = {}

            if code in config["companies"]:
                return JsonResponse(
                    {"error": "公司代碼已存在，無法覆蓋", "existing_company": {code: config["companies"][code]}},
                    status=400
            )

            config["companies"][code] = name
            # 保存更新後的 config.json
            with open(CONFIG_PATH, "w", encoding="utf-8") as file:
                json.dump(config, file, ensure_ascii=False, indent=4)
            # 同步更新 companies_name_code.json
            with open(COMPANIES_PATH, "w", encoding="utf-8") as file:
                json.dump(config["companies"], file, ensure_ascii=False, indent=4)
            if not Company.objects.filter(stock_code=code).exists(): # 如果不存在，新增公司 ，應該不會			有問題 ，因為這裡是找stock_index的csv檔
                Company.objects.create(stock_code=code, name=name)
                print(f"新增公司: {code} (股票代碼: {name})")
            get_single_last_data(code)
            printUnivList(code,10)
            update_csv()
            return JsonResponse({"success": True, "updated_company": {code: name}}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "無效的 JSON 格式"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "僅支持 POST 請求"}, status=405)


def get_stock_index(stock_code):

    company = get_object_or_404(Company, stock_code=stock_code)
    print(company.name)
    if company.stockindex_set.count() <= 0:
        # GO TO THE DATABASE
        print(company.stockindex_set.count(),"進到function拿資料")
        get_crawl_save_data()
       # print("拿資料")

    # DATABASE TO 5 DAYS
    indexs = company.stockindex_set.all().order_by('-Date')[:5].values()
    print(company.stockindex_set.count())
    print(list(indexs))
    return list(indexs)


def home(request): #不要刪 不要刪 台積電 (這樣比較有個進入點)
    recent_data,predict_data = get_hist_predict_data("2330")
    data = {"recent_data":recent_data,"stock_code":"2330","predict_data":predict_data}
    data['indexs'] = get_stock_index("2330")
    try:
        with open(COMPANIES_PATH, "r", encoding="utf-8") as file:
            companies = json.load(file)
    except FileNotFoundError:
        companies = {}
    return render(request,"stock_predict/home.html",{"data":json.dumps(data), "companies": companies}) # json.dumps(list)

def predict_stock_action(request):
    stock_code = request.POST.get('stock_code',None)
    print("stock_code:\n",stock_code)
    
    try:
        with open(COMPANIES_PATH, "r", encoding="utf-8") as file:
            companies = json.load(file)
    except FileNotFoundError:
        companies = {}
    if not Company.objects.filter(stock_code=stock_code).exists(): # 如果不存在，新增公司 ，應該不會有問題 ，因為這裡是找stock_index的csv檔
        Company.objects.create(stock_code=stock_code, name=companies[stock_code])
        print(f"新增公司: {companies[stock_code]} (股票代碼: {stock_code})")
    recent_data, predict_data = get_hist_predict_data(stock_code)
    data = {"recent_data": recent_data, "stock_code": stock_code, "predict_data": predict_data}
    data['indexs'] = get_stock_index(stock_code)
    print(data)
    return render(request, "stock_predict/home.html", {"data": json.dumps(data), "companies": companies})  # json.dumps(list)

sched = Scheduler()
# 定時任務(crontab)
# @sched.interval_schedule(seconds=2)   # 每2s执行一次
@sched.cron_schedule(hour=0,minute=0)   # 每日凌晨调度一次
def train_models():
    run.train_all_stock()
    update_csv()
sched.start()
