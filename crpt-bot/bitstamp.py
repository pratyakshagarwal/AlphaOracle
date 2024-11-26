import json
import requests
import datetime
import pandas as pd
import yfinance as yf

ticker = "BTC-USD"
start = "2024-11-24"
end = "2024-11-25" 
data = yf.download(tickers=ticker, start=start, end=end, interval="1m")

def process_columns(frame:pd.DataFrame) -> pd.DataFrame:
    columns = [col[0] for col in [*frame.columns]]
    frame.columns = columns
    return frame

data = process_columns(data)
print(data.head())
print(data.shape)

data.to_csv(f"{ticker}_data.csv")

import sys;sys.exit()
url = "https://api.binance.com/api/v3/klines"
params = {
    "symbol": "BTCUSDT",
    "interval": "1m",
    "limit": 1440  # Last 24 hours of minute data
}
response = requests.get(url, params=params)
data = response.json()
print(data)