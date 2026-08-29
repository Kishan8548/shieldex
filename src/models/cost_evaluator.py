import numpy as np
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "results"

# Cost matrix (₹ Indian Rupees)
# FN = missed fraud → merchant bears chargeback loss
# FP = blocked legit txn → customer friction/churn cost
COST_FN = 5_000
COST_FP = 150


def compute_cost_at_threshold(y_true, y_prob, threshold, cost_fn=COST_FN, cost_fp=COST_FP):
    y_pred = (y_prob >= threshold).astype(int)
    TP = int(((y_pred == 1) & (y_true == 1)).sum())
    FP = int(((y_pred == 1) & (y_true == 0)).sum())
    TN = int(((y_pred == 0) & (y_true == 0)).sum())
    FN = int(((y_pred == 0) & (y_true == 1)).sum())

    precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "threshold": round(threshold, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "TP": TP, "FP": FP, "TN": TN, "FN": FN,
        "cost_fn_inr": FN * cost_fn,
        "cost_fp_inr": FP * cost_fp,
        "total_cost_inr": FN * cost_fn + FP * cost_fp,
    }


def find_optimal_threshold(y_true, y_prob, cost_fn=COST_FN, cost_fp=COST_FP, n_thresholds=200):
    thresholds = np.linspace(0.01, 0.99, n_thresholds)
    sweep = [compute_cost_at_threshold(y_true, y_prob, t, cost_fn, cost_fp) for t in thresholds]
    best = min(sweep, key=lambda x: x["total_cost_inr"])

    n_fraud = int(y_true.sum())
    n_legit = int((y_true == 0).sum())
    flag_nothing_cost = n_fraud * cost_fn
    flag_everything_cost = n_legit * cost_fp
    default_metrics = compute_cost_at_threshold(y_true, y_prob, 0.5, cost_fn, cost_fp)

    result = {
        "optimal_threshold": best["threshold"],
        "optimal_metrics": best,
        "baselines": {
            "flag_nothing": {"total_cost_inr": flag_nothing_cost, "precision": 0.0, "recall": 0.0},
            "flag_everything": {"total_cost_inr": flag_everything_cost,
                                "precision": float(n_fraud / (n_fraud + n_legit)), "recall": 1.0},
            "threshold_0.5": {"total_cost_inr": default_metrics["total_cost_inr"],
                              "precision": default_metrics["precision"], "recall": default_metrics["recall"]},
        },
        "cost_savings_vs_flag_nothing_inr": flag_nothing_cost - best["total_cost_inr"],
        "cost_savings_vs_flag_everything_inr": flag_everything_cost - best["total_cost_inr"],
        "cost_fn_per_txn_inr": cost_fn,
        "cost_fp_per_txn_inr": cost_fp,
        "full_threshold_sweep": sweep,
    }

    logger.info(f"Optimal threshold: {best['threshold']:.4f} | "
                f"Precision: {best['precision']:.4f} | Recall: {best['recall']:.4f} | "
                f"Cost: ₹{best['total_cost_inr']:,.0f} | "
                f"Saves ₹{flag_nothing_cost - best['total_cost_inr']:,.0f} vs flag-nothing")
    return result


def generate_cost_report(y_val_true, y_val_prob, label="validation", save=True):
    from sklearn.metrics import average_precision_score, roc_auc_score, precision_recall_curve

    result = find_optimal_threshold(y_val_true, y_val_prob)
    result["pr_auc"] = round(float(average_precision_score(y_val_true, y_val_prob)), 4)
    result["roc_auc"] = round(float(roc_auc_score(y_val_true, y_val_prob)), 4)

    prec, rec, thresh = precision_recall_curve(y_val_true, y_val_prob)
    result["pr_curve"] = {
        "precision": [round(float(p), 4) for p in prec.tolist()],
        "recall": [round(float(r), 4) for r in rec.tolist()],
        "thresholds": [round(float(t), 4) for t in thresh.tolist()],
    }

    if save:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        save_result = {k: v for k, v in result.items() if k != "full_threshold_sweep"}
        with open(RESULTS_DIR / f"{label}_cost_analysis.json", "w") as f:
            json.dump(save_result, f, indent=2)

    return result
