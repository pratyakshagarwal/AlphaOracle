import os
import pickle
import requests
import datetime as dt
import bs4 as bs
import yfinance as yf
from typing import List

def save_tickers(link: str, path: str) -> List[str]:
    """
    Fetch the tickers of NIFTY 50 companies from a given Wikipedia page and save them as a pickle file.
    
    Args:
        link (str): URL of the Wikipedia page containing the NIFTY 50 table.
        path (str): Path where the pickle file will be saved.
    
    Returns:
        List[str]: List of tickers with '.NS' suffix for NSE.
    """
    # Fetch the webpage content
    resp = requests.get(link)
    soup = bs.BeautifulSoup(resp.text, "lxml")
    
    # Find the table with tickers
    table = soup.find('table', {'class': 'wikitable sortable'})
    if not table:
        raise ValueError("Could not find the required table on the page.")
    
    tickers = []

    # Extract tickers from the table
    for row in table.findAll('tr')[1:]:  # Skip the header row
        cells = row.findAll('td')
        if len(cells) > 1:  # Check if the row has enough cells
            ticker = cells[1].text.strip()  # Extract the ticker (2nd column)
            tickers.append(ticker)
    
    # Add '.NS' to each ticker to denote NSE stocks
    tickers = [ticker + '.NS' for ticker in tickers]

    # Save the tickers to a pickle file
    os.makedirs('data', exist_ok=True)  # Ensure the directory exists
    with open(f'data/{path}', 'wb') as f:
        pickle.dump(tickers, f)
    
    return tickers


def fetch_data(nifty_reload: bool = False, link: str = None, end: str = '2023-12-31',
               path: str = None) -> None:
    """
    Fetch historical stock data for NIFTY 50 tickers and save it as CSV files.
    
    Args:
        nifty_reload (bool): If True, reload tickers from the given link. Default is False.
        link (str): URL to fetch the tickers from if `nifty_reload` is True.
        end (str): End date for historical stock data in 'YYYY-MM-DD' format. Default is '2023-12-31'.
        path (str): Path to the pickle file storing the tickers.
    """
    if nifty_reload:
        # Reload tickers from the provided link
        tickers = save_tickers(link=link, path=path)
    else:
        # Load tickers from the pickle file
        with open(f'data/{path}', 'rb') as f:
            tickers = pickle.load(f)
    
    # Define the start date for stock data
    start_date = '2008-01-01'
    # Ensure the directory for stock data exists
    os.makedirs('data/stock_dfs', exist_ok=True)

    # Download and save data for each ticker
    for ticker in tickers:
        Tpath = f'data/stock_dfs/{ticker}.csv'
        if not os.path.exists(Tpath):
            # Fetch data from Yahoo Finance
            df = yf.download(ticker, start=start_date, end=end)
            # Ensure column names are strings
            df.columns = [column[0] for column in [*df.columns]]
            df.to_csv(Tpath)
            print(f"Saved {ticker} data at: {Tpath}")
        else:
            print(f"Already have data for {ticker}")


if __name__ == '__main__':pass
