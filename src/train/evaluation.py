import numpy as np
from typing import Dict
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.metrics import f1_score, precision_score, recall_score
import seaborn as sns

def plot_confusion_matrix(y_true:np.ndarray, y_pred:np.ndarray, class_names:Dict, Cpath:str) -> None:
    """
    Plots a confusion matrix using the true labels and predicted labels.
    
    Parameters:
    - y_true: Array-like, true labels
    - y_pred: Array-like, predicted labels
    - class_names: List of class names for labeling the axes
    
    Returns:
    - None
    """
    # Generate confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    # Plot confusion matrix using seaborn heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names)
    
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.savefig(Cpath)
    plt.show()

def plot_roc_curve(y_true:np.ndarray, y_pred_prob:np.ndarray, Rpath:str) -> None:
    """
    Plots the ROC curve and saves the figure to the specified path.
    
    Parameters:
    y_true (array-like): True labels.
    y_pred_prob (array-like): Predicted probabilities (e.g., from a classifier's predict_proba method).
    save_path (str): Path to save the ROC curve plot.
    """
    # Compute the ROC curve and AUC
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_prob)
    roc_auc = auc(fpr, tpr)

    # Plotting the ROC curve
    plt.figure()
    plt.plot(fpr, tpr, color='blue', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')  # Diagonal line
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.legend(loc='lower right')
    
    # Save the plot to the specified path
    plt.savefig(Rpath)
    plt.close()  # Close the plot to avoid displaying it inline
    print(f"ROC curve saved to {Rpath}")

def evaluate_model(y_true, y_pred) -> Dict[str, float]:
    """Evaluate the model using multiple metrics."""
    return {
        "accuracy": np.mean(y_true == y_pred),
        "f1_score": f1_score(y_true, y_pred, average="weighted"),
        "precision": precision_score(y_true, y_pred, average="weighted"),
        "recall": recall_score(y_true, y_pred, average="weighted"),
    }


if __name__ == '__main__':
    pass