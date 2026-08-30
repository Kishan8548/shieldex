import sys
import json
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
from src.data.loader import load_and_prepare, get_feature_columns
from src.data.preprocessor import split_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def run_eda_analysis():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Loading dataset and generating feature distributions...")
    df = load_and_prepare()

    total_txns = int(len(df))
    fraud_txns = int(df["Class"].sum())
    legit_txns = int(total_txns - fraud_txns)
    fraud_rate = float(df["Class"].mean())

    amount_stats = {
        "legit": {
            "mean": round(float(df[df["Class"] == 0]["Amount"].mean()), 2),
            "median": round(float(df[df["Class"] == 0]["Amount"].median()), 2),
            "max": round(float(df[df["Class"] == 0]["Amount"].max()), 2),
            "min": round(float(df[df["Class"] == 0]["Amount"].min()), 2),
        },
        "fraud": {
            "mean": round(float(df[df["Class"] == 1]["Amount"].mean()), 2),
            "median": round(float(df[df["Class"] == 1]["Amount"].median()), 2),
            "max": round(float(df[df["Class"] == 1]["Amount"].max()), 2),
            "min": round(float(df[df["Class"] == 1]["Amount"].min()), 2),
        }
    }

    merchant_agg = df.groupby("merchant_id").agg(
        total_txns=("Class", "count"),
        fraud_txns=("Class", "sum"),
        fraud_rate=("Class", "mean")
    ).reset_index()

    top_merchants = merchant_agg.sort_values("total_txns", ascending=False).head(10).to_dict(orient="records")

    train_df, val_df, test_df = split_dataset(df)

    summary = {
        "dataset_summary": {
            "total_records": total_txns,
            "legit_records": legit_txns,
            "fraud_records": fraud_txns,
            "fraud_rate_percentage": round(fraud_rate * 100, 4),
            "imbalance_ratio": f"1:{int(legit_txns / fraud_txns)}"
        },
        "amount_statistics": amount_stats,
        "splits_summary": {
            "train": {"total": len(train_df), "fraud": int(train_df["Class"].sum()), "fraud_rate": round(float(train_df["Class"].mean()) * 100, 4)},
            "val": {"total": len(val_df), "fraud": int(val_df["Class"].sum()), "fraud_rate": round(float(val_df["Class"].mean()) * 100, 4)},
            "test": {"total": len(test_df), "fraud": int(test_df["Class"].sum()), "fraud_rate": round(float(test_df["Class"].mean()) * 100, 4)}
        },
        "feature_count": len(get_feature_columns()),
        "features": get_feature_columns(),
        "top_10_merchants_by_volume": top_merchants
    }

    out_file = RESULTS_DIR / "eda_summary.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"EDA Summary saved successfully to: {out_file}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run_eda_analysis()
