import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.base import BaseEstimator, TransformerMixin
import logging

from src.data.loader import get_feature_columns

logger = logging.getLogger(__name__)

PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"
MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"

TRAIN_RATIO = 0.70
VAL_RATIO = 0.10
TEST_RATIO = 0.20
RANDOM_SEED = 42


class AmountScaler(BaseEstimator, TransformerMixin):
    """Scales only the Amount column using RobustScaler (handles outlier transactions)."""

    def __init__(self):
        self.scaler = RobustScaler()
        self._amount_idx = None

    def fit(self, X: np.ndarray, y=None):
        feature_cols = get_feature_columns()
        self._amount_idx = feature_cols.index("Amount")
        self.scaler.fit(X[:, self._amount_idx].reshape(-1, 1))
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        X = X.copy()
        X[:, self._amount_idx] = self.scaler.transform(
            X[:, self._amount_idx].reshape(-1, 1)
        ).ravel()
        return X


def split_dataset(df: pd.DataFrame, train_ratio=TRAIN_RATIO, val_ratio=VAL_RATIO,
                  test_ratio=TEST_RATIO, seed=RANDOM_SEED):
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-9

    train_val_df, test_df = train_test_split(
        df, test_size=test_ratio, stratify=df["Class"], random_state=seed
    )
    adjusted_val = val_ratio / (train_ratio + val_ratio)
    train_df, val_df = train_test_split(
        train_val_df, test_size=adjusted_val, stratify=train_val_df["Class"], random_state=seed
    )

    logger.info("Dataset split:")
    for name, split in [("Train", train_df), ("Val", val_df), ("Test [FROZEN]", test_df)]:
        n, f = len(split), split["Class"].sum()
        logger.info(f"  {name:18s}: {n:7,} rows | {f:4} fraud ({f/n*100:.3f}%)")

    return train_df, val_df, test_df


def prepare_features(train_df, val_df, test_df):
    feature_cols = get_feature_columns()

    X_train = train_df[feature_cols].values.astype(np.float32)
    y_train = train_df["Class"].values.astype(np.int32)
    X_val = val_df[feature_cols].values.astype(np.float32)
    y_val = val_df["Class"].values.astype(np.int32)
    X_test = test_df[feature_cols].values.astype(np.float32)
    y_test = test_df["Class"].values.astype(np.int32)

    # Fit scaler on train only — no leakage
    scaler = AmountScaler()
    scaler.fit(X_train)
    X_train = scaler.transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)

    logger.info(f"Shapes — Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
    return X_train, y_train, X_val, y_val, X_test, y_test, scaler


def save_splits(X_train, y_train, X_val, y_val, X_test, y_test, scaler, output_dir=None):
    out = Path(output_dir) if output_dir else PROCESSED_DIR
    out.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(out / "train.npz", X=X_train, y=y_train)
    np.savez_compressed(out / "val.npz", X=X_val, y=y_val)
    np.savez_compressed(out / "test.npz", X=X_test, y=y_test)
    joblib.dump(scaler, MODELS_DIR / "scaler.joblib")
    logger.info(f"Splits saved to {out}/ | Scaler saved to {MODELS_DIR}/")


def load_splits(data_dir=None):
    d = Path(data_dir) if data_dir else PROCESSED_DIR
    train = np.load(d / "train.npz")
    val = np.load(d / "val.npz")
    test = np.load(d / "test.npz")
    return train["X"], train["y"], val["X"], val["y"], test["X"], test["y"]


def load_scaler(models_dir=None):
    m = Path(models_dir) if models_dir else MODELS_DIR
    return joblib.load(m / "scaler.joblib")
