import pickle
import pandas as pd
from tqdm import tqdm

def compile_data(Tpath: str, Dpath: str) -> None:
    """
    Compile adjusted closing prices from multiple stock CSV files into a single DataFrame.

    Args:
        Tpath (str): Path to the pickle file containing the list of tickers.
        Dpath (str): Path to save the compiled CSV file.

    Returns:
        None
    """
    # Load the list of tickers from the pickle file
    with open(f"data/{Tpath}", 'rb') as f:
        tickers = pickle.load(f)

    # Initialize an empty DataFrame to store the compiled data
    main_frame = pd.DataFrame()

    # Loop through each ticker and process its corresponding CSV file
    for ticker in tqdm(tickers, desc="Compiling Data"):
        # Read the CSV file for the current ticker
        frame = pd.read_csv(f"data/stock_dfs/{ticker}.csv")
        frame.set_index('Date', inplace=True)  # Set the 'Date' column as the index

        # Rename 'Adj Close' column to the ticker name
        frame.rename(columns={'Adj Close': f'{ticker}'}, inplace=True)

        # Drop unnecessary columns (e.g., Open, High, Low, Close, Volume)
        frame.drop(columns=['Open', 'High', 'Low', 'Close', 'Volume'], axis=1, inplace=True)

        # Merge the current frame with the main DataFrame
        if main_frame.empty:
            main_frame = frame  # Assign directly if it's the first frame
        else:
            main_frame = main_frame.join(frame, how='outer')  # Join on the index (Date)

    # Save the compiled data as a CSV file
    main_frame.to_csv(f'data/{Dpath}')

if __name__ == '__main__':pass