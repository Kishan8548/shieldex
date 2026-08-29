import time
import math
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class SpikeAlert:
    merchant_id: str
    alert_id: str
    fired_at: str
    z_score: float
    current_fraud_rate: float
    baseline_fraud_rate: float
    transactions_in_window: int
    severity: str  # "WARNING" | "CRITICAL"

    def to_dict(self):
        return asdict(self)


@dataclass
class MerchantState:
    merchant_id: str
    ewma_mean: float = 0.0
    ewma_var: float = 0.0
    n_observations: int = 0
    last_updated: float = field(default_factory=time.time)
    recent_scores: deque = field(default_factory=lambda: deque(maxlen=100))
    active_alert: Optional[str] = None


class SpikeDetector:
    """
    Per-merchant EWMA fraud spike detector.

    Uses exponentially weighted moving average to maintain a per-merchant
    baseline fraud rate. Fires alerts when the z-score of incoming fraud
    scores exceeds the configured threshold.

    Params:
        alpha: EWMA decay factor — higher means more responsive to recent data.
        z_threshold: Z-score to trigger an alert (default 3.0 ~ 3 std devs).
        min_observations: Warm-up period before alerting.
    """

    def __init__(self, alpha=0.15, z_threshold=3.0, min_observations=20):
        self.alpha = alpha
        self.z_threshold = z_threshold
        self.min_observations = min_observations
        self._states: dict[str, MerchantState] = {}
        self._active_alerts: dict[str, SpikeAlert] = {}
        self._alert_history: list[SpikeAlert] = []
        self._alert_counter = 0

    def _get_or_create_state(self, merchant_id):
        if merchant_id not in self._states:
            self._states[merchant_id] = MerchantState(merchant_id=merchant_id)
        return self._states[merchant_id]

    def _update_ewma(self, state: MerchantState, fraud_score: float):
        alpha = self.alpha
        prev_mean = state.ewma_mean
        state.ewma_mean = alpha * fraud_score + (1 - alpha) * state.ewma_mean
        state.ewma_var = (1 - alpha) * (state.ewma_var + alpha * (fraud_score - prev_mean) ** 2)
        state.n_observations += 1
        state.recent_scores.append(fraud_score)
        state.last_updated = time.time()

    def _compute_z_score(self, state: MerchantState, x: float) -> float:
        stddev = math.sqrt(max(state.ewma_var, 1e-9))
        return (x - state.ewma_mean) / stddev

    def _make_alert_id(self):
        self._alert_counter += 1
        return f"ALERT_{self._alert_counter:06d}_{int(time.time())}"

    def update(self, merchant_id: str, fraud_score: float,
               timestamp: Optional[datetime] = None) -> Optional[SpikeAlert]:
        state = self._get_or_create_state(merchant_id)
        pre_update_mean = state.ewma_mean
        self._update_ewma(state, fraud_score)

        if state.n_observations < self.min_observations:
            return None

        z_score = self._compute_z_score(state, fraud_score)

        if merchant_id in self._active_alerts and z_score < self.z_threshold:
            del self._active_alerts[merchant_id]
            state.active_alert = None

        if z_score >= self.z_threshold and merchant_id not in self._active_alerts:
            severity = "CRITICAL" if z_score >= self.z_threshold * 1.5 else "WARNING"
            alert_id = self._make_alert_id()
            alert = SpikeAlert(
                merchant_id=merchant_id,
                alert_id=alert_id,
                fired_at=(timestamp or datetime.utcnow()).isoformat(),
                z_score=round(z_score, 3),
                current_fraud_rate=round(fraud_score, 4),
                baseline_fraud_rate=round(pre_update_mean, 4),
                transactions_in_window=min(state.n_observations, len(state.recent_scores)),
                severity=severity,
            )
            self._active_alerts[merchant_id] = alert
            self._alert_history.append(alert)
            state.active_alert = alert_id
            logger.warning(f"SPIKE [{severity}] {merchant_id} z={z_score:.2f} score={fraud_score:.4f}")
            return alert

        return None

    def get_merchant_stats(self, merchant_id: str) -> dict:
        if merchant_id not in self._states:
            return {"merchant_id": merchant_id, "status": "no_data"}
        state = self._states[merchant_id]
        return {
            "merchant_id": merchant_id,
            "ewma_mean": round(state.ewma_mean, 4),
            "ewma_stddev": round(math.sqrt(max(state.ewma_var, 0)), 4),
            "n_observations": state.n_observations,
            "has_active_alert": merchant_id in self._active_alerts,
            "active_alert": self._active_alerts[merchant_id].to_dict()
                            if merchant_id in self._active_alerts else None,
        }

    def get_all_active_alerts(self) -> list[dict]:
        return [a.to_dict() for a in self._active_alerts.values()]

    def get_alert_history(self, limit=100) -> list[dict]:
        return [a.to_dict() for a in self._alert_history[-limit:]]

    def get_all_merchant_stats(self) -> list[dict]:
        return [self.get_merchant_stats(mid) for mid in self._states]

    def reset_merchant(self, merchant_id: str):
        self._states.pop(merchant_id, None)
        self._active_alerts.pop(merchant_id, None)

    def reset_all(self):
        self._states.clear()
        self._active_alerts.clear()
        self._alert_history.clear()
        self._alert_counter = 0


def evaluate_spike_detector(detector, transactions, injected_burst_merchants, burst_start_indices):
    detector.reset_all()
    true_positives = 0
    false_positives = 0
    detection_latencies = []
    alerted_merchants = set()
    txn_counts_since_burst = {m: 0 for m in injected_burst_merchants}

    for i, txn in enumerate(transactions):
        mid = txn["merchant_id"]
        alert = detector.update(mid, txn["fraud_score"], txn.get("timestamp"))

        if mid in injected_burst_merchants and i >= burst_start_indices.get(mid, 0):
            txn_counts_since_burst[mid] = txn_counts_since_burst.get(mid, 0) + 1

        if alert and mid not in alerted_merchants:
            alerted_merchants.add(mid)
            if mid in injected_burst_merchants:
                true_positives += 1
                detection_latencies.append(txn_counts_since_burst.get(mid, 0))
            else:
                false_positives += 1

    n_burst = len(injected_burst_merchants)
    n_non_burst = len(set(t["merchant_id"] for t in transactions) - injected_burst_merchants)

    return {
        "detection_rate": round(true_positives / n_burst if n_burst > 0 else 0.0, 4),
        "false_alarm_rate": round(false_positives / n_non_burst if n_non_burst > 0 else 0.0, 4),
        "avg_detection_latency_txns": round(
            sum(detection_latencies) / len(detection_latencies) if detection_latencies else float("inf"), 1
        ),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "n_burst_merchants": n_burst,
        "n_non_burst_merchants": n_non_burst,
    }
