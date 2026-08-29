import numpy as np
import json
import logging
from pathlib import Path
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    average_precision_score, roc_auc_score,
    confusion_matrix, precision_recall_curve,
)

logger = logging.getLogger(__name__)
RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "results"


def compute_full_metrics(y_true, y_prob, threshold, cost_fn=5000, cost_fp=150,
                         label="test", save=True):
    y_pred = (y_prob >= threshold).astype(int)

    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    pr_auc = float(average_precision_score(y_true, y_prob))
    roc_auc = float(roc_auc_score(y_true, y_prob))

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    model_cost = int(fn) * cost_fn + int(fp) * cost_fp
    flag_nothing_cost = int(y_true.sum()) * cost_fn
    flag_everything_cost = int((y_true == 0).sum()) * cost_fp
    default_pred = (y_prob >= 0.5).astype(int)
    default_cost = (
        int(((default_pred == 0) & (y_true == 1)).sum()) * cost_fn +
        int(((default_pred == 1) & (y_true == 0)).sum()) * cost_fp
    )

    prec_curve, rec_curve, _ = precision_recall_curve(y_true, y_prob)
    step = max(1, len(prec_curve) // 200)

    metrics = {
        "dataset": label,
        "threshold": round(threshold, 4),
        "n_samples": len(y_true),
        "n_fraud": int(y_true.sum()),
        "n_legit": int((y_true == 0).sum()),
        "fraud_rate_pct": round(float(y_true.mean()) * 100, 3),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "pr_auc": round(pr_auc, 4),
        "roc_auc": round(roc_auc, 4),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
        "cost_matrix": {"fn_cost_per_txn_inr": cost_fn, "fp_cost_per_txn_inr": cost_fp},
        "model_total_cost_inr": model_cost,
        "baselines": {
            "flag_nothing_cost_inr": flag_nothing_cost,
            "flag_everything_cost_inr": flag_everything_cost,
            "threshold_0.5_cost_inr": default_cost,
        },
        "savings_vs_flag_nothing_inr": flag_nothing_cost - model_cost,
        "savings_vs_flag_everything_inr": flag_everything_cost - model_cost,
        "savings_vs_default_threshold_inr": default_cost - model_cost,
        "pr_curve": {
            "precision": [round(float(p), 4) for p in prec_curve[::step].tolist()],
            "recall": [round(float(r), 4) for r in rec_curve[::step].tolist()],
        },
    }

    _log_table(metrics)

    if save:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        save_m = {k: v for k, v in metrics.items() if k != "pr_curve"}
        with open(RESULTS_DIR / f"{label}_metrics.json", "w") as f:
            json.dump(save_m, f, indent=2)
        with open(RESULTS_DIR / f"{label}_pr_curve.json", "w") as f:
            json.dump(metrics["pr_curve"], f)

    return metrics


def _log_table(m):
    logger.info("\n" + "=" * 60)
    logger.info(f"  RESULTS — {m['dataset'].upper()} SET")
    logger.info("=" * 60)
    logger.info(f"  Precision  : {m['precision']:.4f}")
    logger.info(f"  Recall     : {m['recall']:.4f}")
    logger.info(f"  F1         : {m['f1_score']:.4f}")
    logger.info(f"  PR-AUC     : {m['pr_auc']:.4f}")
    logger.info(f"  ROC-AUC    : {m['roc_auc']:.4f}")
    logger.info(f"  TP/FP/TN/FN: {m['true_positives']}/{m['false_positives']}/{m['true_negatives']}/{m['false_negatives']}")
    logger.info(f"  Model cost : ₹{m['model_total_cost_inr']:,.0f}")
    logger.info(f"  Savings    : ₹{m['savings_vs_flag_nothing_inr']:,.0f} vs flag-nothing")
    logger.info("=" * 60)
