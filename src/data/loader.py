import numpy as np
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

RANDOM_SEED = 42
N_MERCHANTS = 50

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def load_raw_dataset(path=None) -> pd.DataFrame:
    csv_path = Path(path) if path else RAW_DIR / "creditcard.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {csv_path}.\n"
            "Download from: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud\n"
            "Place at: data/raw/creditcard.csv"
        )
    logger.info(f"Loading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df):,} rows | Fraud rate: {df['Class'].mean() * 100:.3f}%")
    return df


def add_synthetic_features(df: pd.DataFrame, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """
    Adds synthetic merchant_id and timestamp features.
    NOTE: V1-V28 and Amount are original Kaggle data. merchant_id and timestamp are synthetic.
    """
    rng = np.random.default_rng(seed)
    n = len(df)

    zipf_weights = np.array([1 / (i ** 1.5) for i in range(1, N_MERCHANTS + 1)])
    zipf_weights /= zipf_weights.sum()
    merchant_ids = rng.choice(
        [f"MERCH_{i:03d}" for i in range(1, N_MERCHANTS + 1)],
        size=n,
        p=zipf_weights,
    )
    df = df.copy()
    df["merchant_id"] = merchant_ids

    base_timestamp = pd.Timestamp("2024-01-01 00:00:00")
    time_scaled = df["Time"] / df["Time"].max() * (30 * 24 * 3600)
    df["timestamp"] = base_timestamp + pd.to_timedelta(time_scaled, unit="s")

    df["hour_of_day"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["is_night"] = ((df["hour_of_day"] >= 22) | (df["hour_of_day"] <= 5)).astype(int)

    return df


def add_merchant_aggregate_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["merchant_id", "timestamp"]).copy()

    df["merchant_avg_amount"] = df.groupby("merchant_id")["Amount"].transform(
        lambda x: x.expanding().mean().shift(1).fillna(x.mean())
    )
    df["merchant_txn_count"] = df.groupby("merchant_id").cumcount() + 1
    df["amount_vs_merchant_avg"] = (
        (df["Amount"] - df["merchant_avg_amount"]) /
        (df["merchant_avg_amount"].replace(0, 1))
    )
    return df


def get_feature_columns() -> list[str]:
    pca_features = [f"V{i}" for i in range(1, 29)]
    amount_features = ["Amount"]
    time_features = ["hour_of_day", "day_of_week", "is_weekend", "is_night"]
    merchant_features = ["merchant_avg_amount", "merchant_txn_count", "amount_vs_merchant_avg"]
    return pca_features + amount_features + time_features + merchant_features


def load_and_prepare(path=None) -> pd.DataFrame:
    df = load_raw_dataset(path)
    df = add_synthetic_features(df)
    df = add_merchant_aggregate_features(df)
    return df
