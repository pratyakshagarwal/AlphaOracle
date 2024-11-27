import joblib
import numpy as np
from typing import Tuple
from sklearn.preprocessing import StandardScaler
from sklearn.base import BaseEstimator

def split_data(X: np.ndarray, y: np.ndarray, size: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split the dataset into training and testing sets based on the given size.

    Args:
        X (np.ndarray): Features dataset.
        y (np.ndarray): Target dataset.
        size (float): Fraction of data to use for training (0 < size < 1).

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: 
        Training features, training targets, testing features, testing targets.
    """
    # Calculate the split index
    split_index = int(len(X) * size)

    # Split the features and targets into training and testing sets
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]

    return X_train, y_train, X_test, y_test

def scale_data(features: np.ndarray, Spath: str) -> Tuple[np.ndarray, BaseEstimator]:
    """
    Scale the dataset using StandardScaler and save the scaler for future use.

    Args:
        features (np.ndarray): Dataset to be scaled.
        Spath (str): Path to save the scaler model.

    Returns:
        Tuple[np.ndarray, BaseEstimator]: Scaled dataset and the scaler object.
    """
    # Initialize the StandardScaler
    scaler = StandardScaler()
    # Fit and transform the dataset
    scaled_features = scaler.fit_transform(features)
    # Save the scaler model using joblib
    joblib.dump(scaler, f"models/{Spath}")
    return scaled_features, scaler

class OutlierHandlers:
    """
    A class to handle outliers in datasets by replacing them with the median.
    """
    def __init__(self, Xtrain: np.ndarray, threshold: float) -> None:
        """
        Initialize the handler with training data statistics and a threshold.

        Args:
            Xtrain (np.ndarray): Training data to calculate median, mean, and std deviation.
            threshold (float): Z-score threshold to identify outliers.
        """
        self.threshold = threshold
        # Calculate and store statistics from training data
        self.median_ = np.median(Xtrain, axis=0)
        self.mean_ = np.mean(Xtrain, axis=0)
        self.std_ = np.std(Xtrain, axis=0)

    def handle(self, data: np.ndarray) -> np.ndarray:
        """
        Replace outliers in the dataset with the median values.

        Args:
            data (np.ndarray): Data to process (training or inference data).

        Returns:
            np.ndarray: Data with outliers replaced by median values.
        """
        # Compute Z-scores using training statistics
        zscores = np.abs((data - self.mean_) / np.where(self.std_ == 0, 1, self.std_))

        # Identify indices of outliers where Z-score exceeds the threshold
        outlier_indices = np.where(zscores > self.threshold)

        # Replace outlier values with the median
        for i in outlier_indices[0]:  # Iterate over rows with outliers
            for j in range(data.shape[1]):  # Iterate over columns
                data[i, j] = self.median_[j]

        return data

if __name__ == '__main__':pass