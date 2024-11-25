from collections import Counter
import numpy as np
import pandas as pd
import pickle
from sklearn import neighbors, svm
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.model_selection import cross_validate, train_test_split
from nifty50_data import process_data

def process_data_for_labels(ticker):
    hm_days = 7
    frame = pd.read_csv("data/nifty50_adsclose_joined.csv", index_col=0)
    tickers = frame.columns.values.tolist()
    frame.fillna(0, inplace=True)

    for i in range(1, hm_days+1):
        frame['{}_{}d'.format(ticker, i)] = (frame[ticker].shift(-i) - frame[ticker]) / frame[ticker]
    frame.fillna(0, inplace=True)
    return tickers, frame

def buy_sell_hold(*args):
    cols = [c for c in args]
    requirement = 0.02
    for col in cols:
        if col > requirement: return 1
        if col < -requirement: return -1
    return 0
    
def extract_featuresets(ticker):
    tickers, frame = process_data_for_labels(ticker)

    frame['{}_target'.format(ticker)] = frame[[f'{ticker}_{i}d' for i in range(1, 8)]].apply(
        lambda row: buy_sell_hold(*row), axis=1
    )
    
    vals = frame['{}_target'.format(ticker)].values.tolist()
    str_vals = [str(i) for i in vals]
    print('Data spread:', Counter(str_vals))

    frame.fillna(0, inplace=True)
    frame = frame.replace([np.inf, -np.inf], np.nan)
    frame.dropna(inplace=True)

    frame_vals = frame[[ticker for ticker in tickers]].pct_change()
    frame_vals = frame_vals.replace([np.inf, -np.inf], 0)
    frame_vals.fillna(0, inplace=True)

    X = frame_vals.values
    y = frame['{}_target'.format(ticker)].values

    return X, y, frame

def do_ml(ticker):
    X, y, frame = extract_featuresets(ticker)
    
    # Time-based train-test split (75% train, 25% test)
    split_index = int(len(X) * 0.75)
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]
    
    clf = VotingClassifier([('lsvc', svm.SVC(probability=True)),
                            ('knn', neighbors.KNeighborsClassifier()),
                            ('rfor', RandomForestClassifier())], voting='soft')
    
    clf.fit(X_train, y_train)
    confidence_train = clf.score(X_train, y_train)
    confidence_test = clf.score(X_test, y_test)
    print(f"Train accuracy: {confidence_train:.4f}, Test accuracy: {confidence_test:.4f}")

    # Only add test set predictions to the frame for backtesting
    test_predictions = clf.predict(X_test)
    frame = pd.read_csv(f"data/stock_dfs/{ticker}.csv")
    frame = process_data(frame)
    frame = frame.iloc[split_index:split_index + len(test_predictions)].copy()  # Adjust the frame size
    frame['predictions'] = test_predictions

    return frame



if __name__ == '__main__':
    # tickers, frame = process_data_for_labels('MMM')
    # X, y, frame = extract_featuresets("MMM")
    frame = do_ml('TRENT.NS')
    frame.to_csv("backtesting_nifty50.csv")
    print(frame.head())
    pass