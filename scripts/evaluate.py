import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=== Final Held-Out Test Set Evaluation ===")

    results_path = Path("results") / "test_metrics.json"
    if results_path.exists():
        logger.warning(f"test_metrics.json already exists. Running again will overwrite.")
        logger.warning("Press Enter to continue or Ctrl+C to cancel.")
        try:
            input()
        except KeyboardInterrupt:
            return

    logger.info("[1/4] Loading test split...")
    from src.data.preprocessor import load_splits
    _, _, _, _, X_test, y_test = load_splits()
    logger.info(f"Test: {len(X_test):,} samples, {y_test.sum():,} fraud")

    logger.info("[2/4] Loading ensemble...")
    from src.models.classifier import FraudEnsemble
    ensemble = FraudEnsemble.load()

    logger.info("[3/4] Evaluating on test set...")
    y_prob = ensemble.predict_proba(X_test)
    from src.evaluation.metrics import compute_full_metrics
    metrics = compute_full_metrics(y_true=y_test, y_prob=y_prob,
                                   threshold=ensemble.threshold, label="test", save=True)

    logger.info("[4/4] Spike detector evaluation...")
    _eval_spike()

    logger.info("Evaluation complete. Results saved to results/")


def _eval_spike():
    import numpy as np
    import json
    from src.models.spike_detector import SpikeDetector, evaluate_spike_detector

    rng = np.random.default_rng(999)
    N_NORMAL, N_BURST = 45, 5
    all_merchants = [f"EVAL_{i:03d}" for i in range(N_NORMAL + N_BURST)]
    burst_merchants = set(all_merchants[N_NORMAL:])
    transactions = []
    burst_start_indices = {}

    for mid in all_merchants[:N_NORMAL]:
        for _ in range(200):
            transactions.append({"merchant_id": mid, "fraud_score": float(rng.beta(1, 20))})

    for mid in burst_merchants:
        for _ in range(50):
            transactions.append({"merchant_id": mid, "fraud_score": float(rng.beta(1, 20))})
        burst_start_indices[mid] = len(transactions)
        for _ in range(50):
            transactions.append({"merchant_id": mid, "fraud_score": float(rng.beta(8, 2))})

    rng.shuffle(transactions)
    detector = SpikeDetector(alpha=0.15, z_threshold=3.0, min_observations=20)
    results = evaluate_spike_detector(detector, transactions, burst_merchants, burst_start_indices)

    Path("results").mkdir(exist_ok=True)
    with open("results/spike_detector_metrics.json", "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Spike eval: detection={results['detection_rate']:.1%} "
                f"false_alarm={results['false_alarm_rate']:.1%}")


if __name__ == "__main__":
    main()
