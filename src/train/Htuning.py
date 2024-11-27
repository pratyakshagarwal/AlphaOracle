from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import VotingClassifier
from sklearn.base import BaseEstimator

from typing import Dict, List
import numpy as np
from tqdm import tqdm


class Htuner:
    """
    A hyperparameter tuning utility for multiple classifiers using RandomizedSearchCV.
    
    Attributes:
        classifier_lists (List[BaseEstimator]): List of classifiers to be tuned.
        classifier_parms_lists (List[Dict]): List of parameter grids for the classifiers.
        best_params (Dict): Dictionary storing the best hyperparameters for each classifier.
        tuned_clf (Dict): Dictionary storing the best tuned classifiers.
    """
    def __init__(self, clf_l: List[BaseEstimator], Pcls_l: List[Dict]) -> None:
        """
        Initialize the Htuner class with classifiers and their parameter grids.
        
        Args:
            clf_l (List[BaseEstimator]): List of classifiers.
            Pcls_l (List[Dict]): List of parameter grids corresponding to the classifiers.
        """
        self.classifier_lists = clf_l
        self.classifier_parms_lists = Pcls_l
        self.best_params = {}
        self.tuned_clf = {}

    def tune(self, price: np.ndarray, action: np.ndarray, cv: int = 5, scoring: str = "accuracy", 
             n_iter: int = 10, random_state: int = 42) -> None:
        """
        Perform hyperparameter tuning for each classifier using RandomizedSearchCV.
        
        Args:
            price (np.ndarray): Feature dataset.
            action (np.ndarray): Target labels.
            cv (int): Number of cross-validation folds. Default is 5.
            scoring (str): Scoring metric for evaluation. Default is "accuracy".
            n_iter (int): Number of parameter settings sampled. Default is 10.
            random_state (int): Random seed for reproducibility. Default is 42.
        """
        # Iterate over classifiers and their parameter grids
        for clf, params in tqdm(zip(self.classifier_lists, self.classifier_parms_lists), 
                                total=len(self.classifier_lists), 
                                desc="Tuning classifiers"):
            # Perform RandomizedSearchCV for each classifier
            rscv = RandomizedSearchCV(clf, params, cv=cv, scoring=scoring,
                                      n_iter=n_iter, random_state=random_state)
            rscv.fit(price, action)
            
            # Store the best parameters and the tuned classifier
            self.best_params[f'{clf.__class__.__name__}'] = rscv.best_params_
            self.tuned_clf[f'{clf.__class__.__name__}'] = rscv.best_estimator_

    def get_params(self) -> Dict:
        """
        Retrieve the best hyperparameters for all classifiers.
        
        Returns:
            Dict: Best hyperparameters for each classifier.
        """
        return self.best_params

    def get_best_classifier(self) -> Dict:
        """
        Retrieve the tuned classifiers.
        
        Returns:
            Dict: Best tuned classifiers.
        """
        return self.tuned_clf

    def build_votingclf(self, voting: str = "hard") -> VotingClassifier:
        """
        Build a VotingClassifier using the tuned classifiers.
        
        Args:
            voting (str): Voting strategy ("hard" or "soft"). Default is "hard".
        
        Returns:
            VotingClassifier: A VotingClassifier composed of the tuned classifiers.
        """
        # Create a VotingClassifier using the tuned classifiers
        voting_clf = VotingClassifier(estimators=[(name, clf) for name, clf in self.tuned_clf.items()], voting=voting)
        return voting_clf

if __name__ == '__main__':pass
