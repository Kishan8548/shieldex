import sys
import argparse
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main(args):
    logger.info("=== Fraud-Spike Detector — Training Pipeline ===")

    logger.info("[1/6] Loading data...")
    from src.data.loader import load_and_prepare
    from src.data.preprocessor import split_dataset, prepare_features, save_splits

    df = load_and_prepare()
    train_df, val_df, test_df = split_dataset(df)
    X_train, y_train, X_val, y_val, X_test, y_test, scaler = prepare_features(train_df, val_df, test_df)
    save_splits(X_train, y_train, X_val, y_val, X_test, y_test, scaler)

    logger.info("[2/6] Logistic Regression baseline...")
    from src.models.classifier import train_baseline
    _, baseline_metrics = train_baseline(X_train, y_train, X_val, y_val)

    logger.info(f"[3-4/6] Training ensemble (n_trials={args.n_trials})...")
    from src.models.classifier import build_ensemble
    ensemble = build_ensemble(X_train, y_train, X_val, y_val, n_trials=args.n_trials)

    logger.info("[5/6] Computing cost-optimal threshold on validation set...")
    from src.models.cost_evaluator import generate_cost_report
    y_val_prob = ensemble.predict_proba(X_val)
    cost_report = generate_cost_report(y_val_prob=y_val_prob, y_val_true=y_val, label="validation")
    ensemble.set_threshold(cost_report["optimal_threshold"])

    logger.info("[6/6] Saving models...")
    ensemble.save()

    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    with open(results_dir / "baseline_metrics.json", "w") as f:
        json.dump(baseline_metrics, f, indent=2)

    logger.info(f"Done. Threshold: {cost_report['optimal_threshold']:.4f} | "
                f"Val PR-AUC: {cost_report['pr_auc']:.4f}")
    logger.info("Next: python scripts/evaluate.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-trials", type=int, default=50)
    main(parser.parse_args())
