from decouple import config
from binance.client import Client
import pandas as pd
import pandas_ta as ta
import json
import os
import time
import datetime

# Set up trading parameters
asset = "BTCUSDT"  # The trading pair to monitor (e.g., Bitcoin/USDT)
entry_p = 25       # RSI value below which the bot will buy
exit_p = 74        # RSI value above which the bot will sell

# Initialize Binance client using API keys stored in environment variables
client = Client(config('API_Key'), config('Secret_Key'), testnet=True)

# -------------------------------------------------------------------------------------------------------------------
# Fetch historical price data (klines) for the given asset
def fetch_klines(asset):
    """
    Fetches 1-minute candlestick data for the past hour for a given asset.
    Returns a DataFrame with time and closing prices.
    """
    klines = client.get_historical_klines(asset, Client.KLINE_INTERVAL_1MINUTE, "1 hour ago UTC")
    klines = [[x[0], float(x[4])] for x in klines]  # Extract time and closing price
    klines = pd.DataFrame(klines, columns=["time", "price"])
    klines['time'] = pd.to_datetime(klines['time'], unit="ms")  # Convert time to datetime
    return klines

# -------------------------------------------------------------------------------------------------------------------
# Calculate the RSI (Relative Strength Index) for the asset
def get_rsi(asset):
    """
    Calculates the 14-period RSI for the given asset using the closing prices from fetch_klines.
    Returns the most recent RSI value.
    """
    klines = fetch_klines(asset)
    klines["rsi"] = ta.rsi(close=klines['price'], length=14)  # Calculate RSI
    return klines['rsi'].iloc[-1]  # Return the latest RSI value

# -------------------------------------------------------------------------------------------------------------------
# Create an account file to track bot state
def create_account():
    """
    Creates a JSON file to track the bot's state, including whether it can buy or sell.
    """
    account = {
        "is_buying": True,  # Indicates whether the bot is ready to buy
        "assets": {},       # Placeholder for asset balances
    }
    with open("bot_account.json", "w") as f:
        f.write(json.dumps(account))

# -------------------------------------------------------------------------------------------------------------------
# Log messages to both the console and a log file
def log(msg):
    """
    Logs a message to the console and appends it to a daily log file in the 'logs' directory.
    """
    print(f"LOG: {msg}")
    if not os.path.isdir("logs"):
        os.makedirs("logs")
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    time = now.strftime("%H-%M-%S")

    with open(f"logs/{today}.txt", "a+") as log_file:
        log_file.write(f"{time}: {msg}\n")

# -------------------------------------------------------------------------------------------------------------------
# Log trade details into a CSV file
def trade_log(sym, side, price, amount):
    """
    Logs trade information (symbol, side, price, amount) into a CSV file in the 'trades' directory.
    Creates the directory and file if they don't exist.
    """
    print(f"{side} {amount} {sym} for {price} per")
    if not os.path.isdir("trades"):
        os.mkdir("trades")
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")

    if not os.path.exists(f"trades/{today}.csv"):
        with open(f"trades/{today}.csv", "w") as trade_file:
            trade_file.write("sym,side,amount,price\n")  # Write header

    with open(f"trades/{today}.csv", "a") as trade_file:
        trade_file.write(f"{sym},{side},{amount},{price}\n")

# -------------------------------------------------------------------------------------------------------------------
# Execute a trade
def do_trade(account, client, asset, side, quantity):
    """
    Executes a trade (buy or sell) on Binance and updates the account state.
    Logs the trade details once the order is filled.
    """
    if side == "buy":
        order = client.order_market_buy(symbol=asset, quantity=quantity)
        account["is_buying"] = False  # Switch state to prevent multiple buys
    else:
        order = client.order_market_sell(symbol=asset, quantity=quantity)
        account["is_buying"] = True  # Switch state to allow buying

    order_id = order['orderId']

    # Wait until the order is fully filled
    while order['status'] != "FILLED":
        order = client.get_order(symbol=asset, orderId=order_id)
        time.sleep(1)

    # Calculate the price paid for the filled order
    price_paid = sum([float(fill['price']) * float(fill['qty']) for fill in order['fills']])

    # Log the trade details
    trade_log(asset, side, price_paid, quantity)

    # Update account state in JSON file
    with open("bot_account.json", "w") as f:
        f.write(json.dumps(account))

# -------------------------------------------------------------------------------------------------------------------
# Main trading logic
def main(trade=False):
    """
    Main function to monitor RSI and execute trades based on entry and exit conditions.
    """
    rsi = get_rsi(asset)  # Get initial RSI
    old_rsi = rsi

    while trade:
        try:
            # Load or create the account file
            if not os.path.exists("bot_account.json"):
                create_account()
            with open('bot_account.json') as f:
                account = json.load(f)

            # Update RSI values
            old_rsi = rsi
            rsi = get_rsi(asset)

            # Execute trades based on RSI thresholds
            if account['is_buying']:
                if rsi < entry_p and old_rsi > entry_p:  # RSI crosses below entry point
                    do_trade(account, client, asset, "buy", quantity=0.01)
            else:
                if rsi > exit_p and old_rsi < exit_p:  # RSI crosses above exit point
                    do_trade(account, client, asset, "sell", quantity=0.01)

            # Log the current status
            balance = client.get_asset_balance(asset="BTC")
            msg = f"asset: {asset}, rsi: {rsi:.4f}, balance: {balance}"
            log(msg)
            time.sleep(10)  # Wait before the next check

        except Exception as e:
            log("ERROR: " + str(e))  # Log any errors

# Entry point for the script
if __name__ == '__main__':
    main(trade=True)
