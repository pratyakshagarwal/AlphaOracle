import os
import pickle
import requests
import bs4 as bs
import pandas as pd
import yfinance as yf
import datetime as dt 
from tqdm import tqdm
import matplotlib.pyplot as plt 
from matplotlib import style
import seaborn as sns
style.use('ggplot')

LINK = "https://en.wikipedia.org/wiki/NIFTY_50"

def save_nifty_tickers(link: str):
    # Fetch the webpage
    resp = requests.get(link)
    soup = bs.BeautifulSoup(resp.text, "lxml")
    
    # Find the table with class 'wikitable sortable'
    table = soup.find('table', {'class': 'wikitable sortable'})
    if not table:
        raise ValueError("Could not find the required table on the page.")
    
    tickers = []
    
    # Loop through the table rows and extract tickers
    for row in table.findAll('tr')[1:]:  # Skip the header row
        cells = row.findAll('td')
        if len(cells) > 1:  # Ensure there are enough cells
            ticker = cells[1].text.strip()  # Extract the ticker (2nd column)
            tickers.append(ticker)
    
    # add .NS at the end of every ticker
    for i in range(len(tickers)):
        tickers[i] = tickers[i] + '.NS'

    # Save the tickers as a pickle file
    with open('data/nifty50_list.pickle', 'wb') as f:
        pickle.dump(tickers, f)
    
    return tickers

def process_data(df):
    df = df.drop([0, 1])
    df.columns = ['Date', 'Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume']
    df = df.reset_index(drop=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.dropna()  
    return df


def fetch_nifty_data(nifty_reload:bool=False, end:str='2023-12-31'):
    if nifty_reload:
        tickers = save_nifty_tickers(link=LINK)
    else:
        with open('data/nifty50_list.pickle', 'rb') as f:
            tickers = pickle.load(f)
        
    strt = '2008-01-01'
    if not os.path.exists('data/stock_dfs'):
        os.makedirs('data/stock_dfs')

    for ticker in tickers:
        Tpath = 'data/stock_dfs/{}.csv'.format(ticker)
        if not os.path.exists(Tpath):
            df = yf.download(ticker, start=strt, end=end)
            df.to_csv(Tpath)
            print(f"Saved {ticker} data at: {Tpath}")
        else:
            print('Already have {}'.format(ticker))

def compile_data():
    with open("data/nifty50_list.pickle", 'rb') as f:
        tickers = pickle.load(f)

    main_frame = pd.DataFrame()
    for ticker in tqdm(tickers, desc="Compiling Data"):
        frame = pd.read_csv(f"data/stock_dfs/{ticker}.csv")
        frame = process_data(df=frame)
        frame.set_index('Date', inplace=True)

        frame.rename(columns={'Adj Close': f'{ticker}'}, inplace=True)
        frame.drop(columns=['Open', 'High', 'Low', 'Close', 'Volume'], axis=1, inplace=True)

        if main_frame.empty:
            main_frame = frame
        else:
            main_frame = main_frame.join(frame, how='outer')

    main_frame.to_csv('data/nifty50_adsclose_joined.csv')

def visualize_data():
    frame = pd.read_csv("data/nifty50_adsclose_joined.csv").drop("Date", axis=1)

    df_corr = frame.corr()
    plt.figure(figsize=(20, 20))
    sns.heatmap(df_corr, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
    plt.savefig("figures/nifty50corr.png")
    plt.show()

if __name__ == '__main__':
    # tickers = save_nifty_tickers(link=LINK)
    # print(tickers)
    # fetch_nifty_data(nifty_reload=True)
    # compile_data()
    visualize_data()