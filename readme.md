# Django 股票預測與捷運資訊系統網頁

這是一個基於 Django 框架開發的網頁應用，主要由兩個部分：「股票預測 (stock_predict)」與「捷運資訊 (MRT)」。

### 1. 股票預測系統 (`stock_predict`)

本系統使用 **LSTM（Long Short-Term Memory）神經網路模型**進行股票趨勢預測，模型訓練所使用的特徵包含 **開盤價（Open）、收盤價（Close）、最高價（High）與最低價（Low）**。

使用者可輸入台股代碼新增股票資料，系統會透過 **yfinance** 套件自動抓取歷史股價資料，並進行模型訓練與預測。

此外，系統整合 **TA-Lib** 技術分析套件，計算多種金融指標，如 **RSI、SMA50、SMA200** 等，並依據這些指標進行綜合評分，提供使用者直觀的投資建議（買入／賣出）。


# 環境安裝 Installation

建議環境: **Miniconda / Anaconda**


安裝 **Miniconda (linux)**
``` bash
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh --output anaconda.sh
mv anaconda.sh /tmp
cd /tmp4.bash anaconda.sh
```

建立conda環境:

``` bash
conda env create --file environment.yml
```

啟動conda環境:

``` bash
conda activate cchh
```

# 運行網頁伺服器 Run the Project

``` bash
cd stockDjango
python manage.py runserver 0.0.0.0:8000
```

# 網頁 Web Pages

Stock Prediction

    http://<IP>:8000/stock_predict/home/

MRT Information

    http://<IP>:8000/MRT/

### 操作的流程圖(1)
<img width="2037" height="1145" alt="image" src="https://github.com/user-attachments/assets/6a33036e-d55d-4e7c-969b-25f6f9a7d2dd" />

### 操作的流程圖(2)
<img width="2027" height="1137" alt="image" src="https://github.com/user-attachments/assets/4fbc1327-5c43-494b-962e-83a35261cdef" />

### 預測網站的示意圖
<img width="2157" height="1090" alt="image" src="https://github.com/user-attachments/assets/dcd48e0c-bb8c-486e-9ff7-b0c8aaf589c5" />

### 基於TA-lib分析出的指標
<img width="1151" height="1087" alt="image" src="https://github.com/user-attachments/assets/4cef61cf-e08a-4d98-b43a-3e0f33cde261" />



# debug(後端神經網路選擇錯誤)
要解決的問題通常會有後端神經網路keras選擇的是theano，所以要開python把全域變數變成tensorflow就可解決這個問題

``` bash
import os
os.environ['KERAS_BACKEND'] = 'tensorflow'
```
