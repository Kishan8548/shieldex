"""
Pydantic request/response schemas for the Fraud-Spike Detector API.

Using Pydantic v2 for strict input validation — malformed transactions
cannot crash the inference pipeline.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# Request schemas
# ─────────────────────────────────────────────────────────────────────────────

class TransactionRequest(BaseModel):
    """
    Single transaction to score. V1–V28 are the anonymized PCA components
    from the Kaggle credit card dataset. In production, these would be
    the normalized feature vector from the merchant's payment gateway.
    """
    # Original Kaggle PCA features (required)
    V1: float; V2: float; V3: float; V4: float; V5: float
    V6: float; V7: float; V8: float; V9: float; V10: float
    V11: float; V12: float; V13: float; V14: float; V15: float
    V16: float; V17: float; V18: float; V19: float; V20: float
    V21: float; V22: float; V23: float; V24: float; V25: float
    V26: float; V27: float; V28: float

    # Transaction amount (must be non-negative)
    Amount: float = Field(..., ge=0, description="Transaction amount in INR")

    # Merchant context (synthetic in demo, real in production)
    merchant_id: str = Field(..., min_length=1, max_length=50)
    timestamp: Optional[datetime] = Field(default=None, description="Transaction timestamp (defaults to now)")

    # Optional time features (computed from timestamp if not provided)
    hour_of_day: Optional[int] = Field(default=None, ge=0, le=23)
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)

    @field_validator("Amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Transaction amount cannot be negative")
        return v

    model_config = {"json_schema_extra": {
        "example": {
            "V1": -1.359807134, "V2": -0.072781173, "V3": 2.536346738,
            "V4": 1.378155224, "V5": -0.338320770, "V6": 0.462387778,
            "V7": 0.239598554, "V8": 0.098697901, "V9": 0.363786970,
            "V10": 0.090794172, "V11": -0.551599533, "V12": -0.617800856,
            "V13": -0.991389847, "V14": -0.311169354, "V15": 1.468176972,
            "V16": -0.470400525, "V17": 0.207971242, "V18": 0.025790631,
            "V19": 0.403992960, "V20": 0.251412098, "V21": -0.018306778,
            "V22": 0.277837576, "V23": -0.110473910, "V24": 0.066928075,
            "V25": 0.128539358, "V26": -0.189114844, "V27": 0.133558377,
            "V28": -0.021053053, "Amount": 149.62,
            "merchant_id": "MERCH_001",
        }
    }}


class BatchTransactionRequest(BaseModel):
    """Batch of transactions for bulk inference (max 100)."""
    transactions: list[TransactionRequest] = Field(..., min_length=1, max_length=100)


# ─────────────────────────────────────────────────────────────────────────────
# Response schemas
# ─────────────────────────────────────────────────────────────────────────────

class ShapFeature(BaseModel):
    """A single feature's SHAP contribution to the prediction."""
    feature: str
    shap_value: float


class SpikeAlertResponse(BaseModel):
    """Active spike alert for a merchant."""
    merchant_id: str
    alert_id: str
    fired_at: str
    z_score: float
    current_fraud_rate: float
    baseline_fraud_rate: float
    transactions_in_window: int
    severity: str  # "WARNING" | "CRITICAL"


class PredictionResponse(BaseModel):
    """Full prediction response for a single transaction."""
    merchant_id: str
    fraud_score: float = Field(..., ge=0, le=1, description="Fraud probability [0, 1]")
    is_fraud: bool
    confidence: str          # "HIGH" | "MEDIUM" | "LOW"
    threshold_used: float
    spike_alert: Optional[SpikeAlertResponse] = None
    top_features: list[ShapFeature]
    latency_ms: float


class BatchPredictionResponse(BaseModel):
    """Response for batch inference."""
    predictions: list[PredictionResponse]
    batch_size: int
    total_flagged: int
    total_alerts: int
    latency_ms: float


class CostBaseline(BaseModel):
    description: str
    total_cost_inr: float
    precision: Optional[float] = None
    recall: Optional[float] = None


class MetricsResponse(BaseModel):
    """Full evaluation metrics response."""
    dataset: str
    threshold: float
    n_samples: int
    n_fraud: int
    n_legit: int
    fraud_rate_pct: float
    precision: float
    recall: float
    f1_score: float
    pr_auc: float
    roc_auc: float
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    model_total_cost_inr: float
    savings_vs_flag_nothing_inr: float
    savings_vs_flag_everything_inr: float
    baselines: dict
    pr_curve: Optional[dict] = None


class MerchantStatsResponse(BaseModel):
    """Per-merchant EWMA statistics for the dashboard."""
    merchant_id: str
    ewma_mean: float
    ewma_stddev: float
    n_observations: int
    has_active_alert: bool
    active_alert: Optional[SpikeAlertResponse] = None


class HealthResponse(BaseModel):
    """API health check."""
    status: str
    models_loaded: bool
    metrics_loaded: bool
    n_active_alerts: int
    version: str = "1.0.0"
