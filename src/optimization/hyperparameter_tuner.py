"""
Hyperparameter Optimization using Optuna

Provides automated hyperparameter tuning for LightGBM, XGBoost, and CatBoost models.
Uses Optuna's TPE sampler for efficient Bayesian optimization.
"""

from __future__ import annotations

from typing import Any

import catboost as cb
import lightgbm as lgb
import optuna
import xgboost as xgb
from optuna.pruners import MedianPruner
from optuna.samplers import TPESampler
from sklearn.model_selection import cross_val_score


class HyperparameterTuner:
    """
    Optuna-based hyperparameter tuning for ensemble models.

    Supports:
    - LightGBM
    - XGBoost
    - CatBoost

    Uses Tree-structured Parzen Estimator (TPE) for efficient search.
    """

    def __init__(
        self,
        model_type: str,
        n_trials: int = 100,
        cv_folds: int = 5,
        metric: str = "neg_log_loss",
        random_state: int = 42,
        n_jobs: int = -1,
    ):
        """
        Initialize hyperparameter tuner.

        Args:
            model_type: One of 'lightgbm', 'xgboost', 'catboost'
            n_trials: Number of optimization trials
            cv_folds: Number of cross-validation folds
            metric: Scoring metric for optimization
            random_state: Random seed for reproducibility
            n_jobs: Number of parallel jobs (-1 = all cores)
        """
        self.model_type = model_type.lower()
        self.n_trials = n_trials
        self.cv_folds = cv_folds
        self.metric = metric
        self.random_state = random_state
        self.n_jobs = n_jobs

        self.study: optuna.Study | None = None
        self.best_params: dict[str, Any] | None = None
        self.best_score: float | None = None

        # Validate model type
        valid_types = ["lightgbm", "xgboost", "catboost"]
        if self.model_type not in valid_types:
            raise ValueError(f"model_type must be one of {valid_types}")

    def _objective_lightgbm(self, trial: optuna.Trial, X, y) -> float:
        """Define hyperparameter search space for LightGBM."""
        params = {
            "objective": "binary",
            "metric": "binary_logloss",
            "boosting_type": trial.suggest_categorical(
                "boosting_type", ["gbdt", "dart"]
            ),
            "num_leaves": trial.suggest_int("num_leaves", 20, 150),
            "max_depth": trial.suggest_int("max_depth", 3, 12),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
            "min_child_samples": trial.suggest_int("min_child_samples", 10, 100),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
            "random_state": self.random_state,
            "verbose": -1,
        }

        model = lgb.LGBMClassifier(**params)
        score = cross_val_score(
            model, X, y, cv=self.cv_folds, scoring=self.metric, n_jobs=self.n_jobs
        ).mean()

        return score

    def _objective_xgboost(self, trial: optuna.Trial, X, y) -> float:
        """Define hyperparameter search space for XGBoost."""
        params = {
            "objective": "binary:logistic",
            "eval_metric": "logloss",
            "booster": trial.suggest_categorical("booster", ["gbtree", "dart"]),
            "max_depth": trial.suggest_int("max_depth", 3, 12),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "gamma": trial.suggest_float("gamma", 1e-8, 1.0, log=True),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
            "random_state": self.random_state,
            "tree_method": "hist",
        }

        model = xgb.XGBClassifier(**params)
        score = cross_val_score(
            model, X, y, cv=self.cv_folds, scoring=self.metric, n_jobs=self.n_jobs
        ).mean()

        return score

    def _objective_catboost(self, trial: optuna.Trial, X, y) -> float:
        """Define hyperparameter search space for CatBoost."""
        params = {
            "loss_function": "Logloss",
            "iterations": trial.suggest_int("iterations", 100, 1000),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "depth": trial.suggest_int("depth", 3, 10),
            "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1e-8, 10.0, log=True),
            "bootstrap_type": trial.suggest_categorical(
                "bootstrap_type", ["Bayesian", "Bernoulli", "MVS"]
            ),
            "random_state": self.random_state,
            "verbose": False,
        }

        # Add bootstrap-specific parameters
        if params["bootstrap_type"] == "Bayesian":
            params["bagging_temperature"] = trial.suggest_float(
                "bagging_temperature", 0, 10
            )
        elif params["bootstrap_type"] == "Bernoulli":
            params["subsample"] = trial.suggest_float("subsample", 0.6, 1.0)

        model = cb.CatBoostClassifier(**params)
        score = cross_val_score(
            model, X, y, cv=self.cv_folds, scoring=self.metric, n_jobs=self.n_jobs
        ).mean()

        return score

    def optimize(self, X, y, verbose: bool = True) -> dict[str, Any]:
        """
        Run hyperparameter optimization.

        Args:
            X: Training features
            y: Training labels
            verbose: Whether to show optimization progress

        Returns:
            Dictionary of best hyperparameters
        """
        # Select objective function based on model type
        objective_map = {
            "lightgbm": self._objective_lightgbm,
            "xgboost": self._objective_xgboost,
            "catboost": self._objective_catboost,
        }

        objective_fn = objective_map[self.model_type]

        # Create Optuna study
        sampler = TPESampler(seed=self.random_state)
        pruner = MedianPruner(n_startup_trials=5, n_warmup_steps=10)

        self.study = optuna.create_study(
            direction="maximize", sampler=sampler, pruner=pruner
        )

        # Optimize
        if verbose:
            print(f"Starting {self.model_type.upper()} optimization...")
            print(
                f"Trials: {self.n_trials}, CV Folds: {self.cv_folds}, Metric: {self.metric}"
            )

        self.study.optimize(
            lambda trial: objective_fn(trial, X, y),
            n_trials=self.n_trials,
            show_progress_bar=verbose,
        )

        # Store results
        self.best_params = self.study.best_params
        self.best_score = self.study.best_value

        if verbose:
            print("\nOptimization complete!")
            print(f"Best score: {self.best_score:.6f}")
            print(f"Best parameters: {self.best_params}")

        return self.best_params

    def get_best_model(self, **kwargs):
        """
        Get model instance with best hyperparameters.

        Args:
            **kwargs: Additional parameters to override

        Returns:
            Trained model instance
        """
        if self.best_params is None:
            raise ValueError("Must run optimize() first")

        # Merge best params with overrides
        params = {**self.best_params, **kwargs}

        # Create model with best parameters
        if self.model_type == "lightgbm":
            params.setdefault("objective", "binary")
            params.setdefault("metric", "binary_logloss")
            params.setdefault("verbose", -1)
            return lgb.LGBMClassifier(**params)

        elif self.model_type == "xgboost":
            params.setdefault("objective", "binary:logistic")
            params.setdefault("eval_metric", "logloss")
            params.setdefault("tree_method", "hist")
            return xgb.XGBClassifier(**params)

        elif self.model_type == "catboost":
            params.setdefault("loss_function", "Logloss")
            params.setdefault("verbose", False)
            return cb.CatBoostClassifier(**params)

    def plot_optimization_history(self):
        """Plot optimization history."""
        if self.study is None:
            raise ValueError("Must run optimize() first")

        return optuna.visualization.plot_optimization_history(self.study)

    def plot_param_importances(self):
        """Plot hyperparameter importances."""
        if self.study is None:
            raise ValueError("Must run optimize() first")

        return optuna.visualization.plot_param_importances(self.study)

    def get_optimization_summary(self) -> dict[str, Any]:
        """
        Get summary of optimization results.

        Returns:
            Dictionary with optimization statistics
        """
        if self.study is None:
            raise ValueError("Must run optimize() first")

        return {
            "best_score": self.best_score,
            "best_params": self.best_params,
            "n_trials": len(self.study.trials),
            "best_trial": self.study.best_trial.number,
            "optimization_time": sum(
                t.duration.total_seconds() for t in self.study.trials if t.duration
            ),
        }
