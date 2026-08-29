import numpy as np
import joblib
import logging
import json
from pathlib import Path

import lightgbm as lgb
import xgboost as xgb
import optuna
import shap
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score

logger = logging.getLogger(__name__)
optuna.logging.set_verbosity(optuna.logging.WARNING)

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"


def train_baseline(X_train, y_train, X_val, y_val):
    logger.info("Training Logistic Regression baseline...")
    model = LogisticRegression(
        class_weight="balanced", max_iter=1000, C=0.1, solver="lbfgs", random_state=42
    )
    model.fit(X_train, y_train)
    y_prob = model.predict_proba(X_val)[:, 1]
    pr_auc = average_precision_score(y_val, y_prob)
    logger.info(f"Baseline — Val PR-AUC: {pr_auc:.4f}")
    return model, {"pr_auc": pr_auc, "model": "logistic_regression"}


def tune_lightgbm(X_train, y_train, X_val, y_val, n_trials=50):
    scale_pos_weight = float((y_train == 0).sum()) / float((y_train == 1).sum())

    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
            "num_leaves": trial.suggest_int("num_leaves", 15, 127),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "min_child_samples": trial.suggest_int("min_child_samples", 5, 100),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
            "scale_pos_weight": scale_pos_weight,
            "objective": "binary",
            "verbose": -1,
            "random_state": 42,
            "n_jobs": -1,
        }
        model = lgb.LGBMClassifier(**params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(period=-1)],
        )
        return average_precision_score(y_val, model.predict_proba(X_val)[:, 1])

    logger.info(f"Tuning LightGBM ({n_trials} trials)...")
    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)

    best_params = {**study.best_params, "scale_pos_weight": scale_pos_weight,
                   "objective": "binary", "verbose": -1, "random_state": 42, "n_jobs": -1}
    best_model = lgb.LGBMClassifier(**best_params)
    best_model.fit(X_train, y_train)

    pr_auc = average_precision_score(y_val, best_model.predict_proba(X_val)[:, 1])
    logger.info(f"LightGBM — Best Val PR-AUC: {pr_auc:.4f}")
    return best_model, best_params, {"pr_auc": pr_auc, "model": "lightgbm"}


def tune_xgboost(X_train, y_train, X_val, y_val, n_trials=50):
    scale_pos_weight = float((y_train == 0).sum()) / float((y_train == 1).sum())

    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
            "max_depth": trial.suggest_int("max_depth", 3, 8),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "gamma": trial.suggest_float("gamma", 0, 5),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
            "scale_pos_weight": scale_pos_weight,
            "eval_metric": "aucpr",
            "random_state": 42,
            "n_jobs": -1,
            "verbosity": 0,
        }
        model = xgb.XGBClassifier(**params)
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)],
                  early_stopping_rounds=50, verbose=False)
        return average_precision_score(y_val, model.predict_proba(X_val)[:, 1])

    logger.info(f"Tuning XGBoost ({n_trials} trials)...")
    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)

    best_params = {**study.best_params, "scale_pos_weight": scale_pos_weight,
                   "eval_metric": "aucpr", "random_state": 42, "n_jobs": -1, "verbosity": 0}
    best_model = xgb.XGBClassifier(**best_params)
    best_model.fit(X_train, y_train)

    pr_auc = average_precision_score(y_val, best_model.predict_proba(X_val)[:, 1])
    logger.info(f"XGBoost — Best Val PR-AUC: {pr_auc:.4f}")
    return best_model, best_params, {"pr_auc": pr_auc, "model": "xgboost"}


class FraudEnsemble:
    """Weighted soft-voting ensemble of LightGBM + XGBoost with SHAP explanations."""

    def __init__(self, lgb_model, xgb_model, lgb_weight: float, xgb_weight: float):
        self.lgb_model = lgb_model
        self.xgb_model = xgb_model
        self.threshold = 0.5
        total = lgb_weight + xgb_weight
        self._w_lgb = lgb_weight / total
        self._w_xgb = xgb_weight / total
        self._lgb_explainer = None
        self._xgb_explainer = None
        logger.info(f"Ensemble weights — LGB: {self._w_lgb:.3f}, XGB: {self._w_xgb:.3f}")

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        p_lgb = self.lgb_model.predict_proba(X)[:, 1]
        p_xgb = self.xgb_model.predict_proba(X)[:, 1]
        return self._w_lgb * p_lgb + self._w_xgb * p_xgb

    def predict(self, X: np.ndarray) -> np.ndarray:
        return (self.predict_proba(X) >= self.threshold).astype(int)

    def predict_single(self, x: np.ndarray) -> dict:
        X = x.reshape(1, -1)
        fraud_score = float(self.predict_proba(X)[0])
        is_fraud = fraud_score >= self.threshold
        shap_vals = self._explain_single(X)
        return {
            "fraud_score": fraud_score,
            "is_fraud": is_fraud,
            "threshold_used": self.threshold,
            "shap_values": shap_vals,
        }

    def _init_explainers(self):
        if self._lgb_explainer is None:
            self._lgb_explainer = shap.TreeExplainer(self.lgb_model)
        if self._xgb_explainer is None:
            self._xgb_explainer = shap.TreeExplainer(self.xgb_model)

    def _explain_single(self, X: np.ndarray) -> list[dict]:
        from src.data.loader import get_feature_columns
        self._init_explainers()
        shap_lgb = self._lgb_explainer.shap_values(X)
        shap_xgb = self._xgb_explainer.shap_values(X)
        if isinstance(shap_lgb, list):
            shap_lgb = shap_lgb[1]
        combined = self._w_lgb * shap_lgb[0] + self._w_xgb * shap_xgb[0]
        pairs = sorted(zip(get_feature_columns(), combined.tolist()),
                       key=lambda x: abs(x[1]), reverse=True)[:10]
        return [{"feature": f, "shap_value": round(v, 5)} for f, v in pairs]

    def set_threshold(self, threshold: float):
        self.threshold = threshold
        logger.info(f"Threshold updated to {threshold:.4f}")

    def save(self, output_dir=None):
        out = Path(output_dir) if output_dir else MODELS_DIR
        out.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.lgb_model, out / "lgb_model.joblib")
        joblib.dump(self.xgb_model, out / "xgb_model.joblib")
        with open(out / "ensemble_meta.json", "w") as f:
            json.dump({"lgb_weight": self._w_lgb, "xgb_weight": self._w_xgb,
                       "threshold": self.threshold}, f, indent=2)
        logger.info(f"Ensemble saved to {out}/")

    @classmethod
    def load(cls, model_dir=None):
        m = Path(model_dir) if model_dir else MODELS_DIR
        lgb_model = joblib.load(m / "lgb_model.joblib")
        xgb_model = joblib.load(m / "xgb_model.joblib")
        with open(m / "ensemble_meta.json") as f:
            meta = json.load(f)
        ensemble = cls(lgb_model, xgb_model, meta["lgb_weight"], meta["xgb_weight"])
        ensemble.threshold = meta["threshold"]
        logger.info(f"Ensemble loaded — threshold: {ensemble.threshold:.4f}")
        return ensemble


def build_ensemble(X_train, y_train, X_val, y_val, n_trials=50) -> FraudEnsemble:
    lgb_model, _, lgb_metrics = tune_lightgbm(X_train, y_train, X_val, y_val, n_trials)
    xgb_model, _, xgb_metrics = tune_xgboost(X_train, y_train, X_val, y_val, n_trials)
    ensemble = FraudEnsemble(lgb_model, xgb_model, lgb_metrics["pr_auc"], xgb_metrics["pr_auc"])
    pr_auc = average_precision_score(y_val, ensemble.predict_proba(X_val))
    logger.info(f"Ensemble Val PR-AUC: {pr_auc:.4f}")
    return ensemble
