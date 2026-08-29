"""
FastAPI routers — predict endpoint.
"""

import time
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from src.api.schemas import (
    TransactionRequest, BatchTransactionRequest,
    PredictionResponse, BatchPredictionResponse,
    ShapFeature, SpikeAlertResponse,
)
from src.api.state import get_app_state

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Prediction"])


def _confidence_label(score: float, threshold: float) -> str:
    margin = abs(score - threshold)
    if margin > 0.3:
        return "HIGH"
    elif margin > 0.1:
        return "MEDIUM"
    return "LOW"


def _build_prediction_response(
    request: TransactionRequest,
    fraud_score: float,
    is_fraud: bool,
    shap_vals: list[dict],
    spike_alert,
    threshold: float,
    latency_ms: float,
) -> PredictionResponse:
    alert_resp = None
    if spike_alert:
        alert_resp = SpikeAlertResponse(**spike_alert.to_dict())

    return PredictionResponse(
        merchant_id=request.merchant_id,
        fraud_score=round(fraud_score, 4),
        is_fraud=is_fraud,
        confidence=_confidence_label(fraud_score, threshold),
        threshold_used=threshold,
        spike_alert=alert_resp,
        top_features=[ShapFeature(**sv) for sv in (shap_vals or [])],
        latency_ms=round(latency_ms, 2),
    )


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Score a single transaction for fraud",
    description=(
        "Runs the transaction through the LightGBM+XGBoost ensemble classifier, "
        "updates the per-merchant EWMA spike detector, and returns the fraud score "
        "with SHAP explanations and any active spike alert."
    ),
)
async def predict_transaction(request: TransactionRequest):
    state = get_app_state()
    if not state.ensemble:
        raise HTTPException(status_code=503, detail="Models not loaded. Run training first.")

    start = time.perf_counter()
    try:
        import numpy as np
        from src.data.loader import get_feature_columns

        # Build feature vector in the correct column order
        feature_cols = get_feature_columns()
        req_dict = request.model_dump()

        # Fill time features from timestamp if not provided
        ts = request.timestamp or datetime.utcnow()
        if request.hour_of_day is None:
            req_dict["hour_of_day"] = ts.hour
        if request.day_of_week is None:
            req_dict["day_of_week"] = ts.weekday()
        req_dict["is_weekend"] = int(ts.weekday() >= 5)
        req_dict["is_night"] = int(ts.hour >= 22 or ts.hour <= 5)

        # Merchant aggregate features — use live state or defaults
        merchant_stats = state.spike_detector.get_merchant_stats(request.merchant_id)
        req_dict["merchant_avg_amount"] = merchant_stats.get("ewma_mean", request.Amount) or request.Amount
        req_dict["merchant_txn_count"] = merchant_stats.get("n_observations", 1) or 1
        avg = req_dict["merchant_avg_amount"] or 1.0
        req_dict["amount_vs_merchant_avg"] = (request.Amount - avg) / max(avg, 1.0)

        x = np.array([req_dict.get(col, 0.0) for col in feature_cols], dtype=np.float32)
        x = state.scaler.transform(x.reshape(1, -1))[0]

        result = state.ensemble.predict_single(x)

        # Update spike detector
        alert = state.spike_detector.update(
            merchant_id=request.merchant_id,
            fraud_score=result["fraud_score"],
            timestamp=ts,
        )

        latency_ms = (time.perf_counter() - start) * 1000

        return _build_prediction_response(
            request=request,
            fraud_score=result["fraud_score"],
            is_fraud=result["is_fraud"],
            shap_vals=result["shap_values"],
            spike_alert=alert,
            threshold=state.ensemble.threshold,
            latency_ms=latency_ms,
        )

    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    summary="Score a batch of transactions",
    description="Batch inference for up to 100 transactions. More efficient than repeated single calls.",
)
async def predict_batch(request: BatchTransactionRequest):
    state = get_app_state()
    if not state.ensemble:
        raise HTTPException(status_code=503, detail="Models not loaded.")

    start = time.perf_counter()
    predictions = []
    total_alerts = 0

    for txn_req in request.transactions:
        resp = await predict_transaction(txn_req)
        predictions.append(resp)
        if resp.spike_alert:
            total_alerts += 1

    latency_ms = (time.perf_counter() - start) * 1000

    return BatchPredictionResponse(
        predictions=predictions,
        batch_size=len(predictions),
        total_flagged=sum(1 for p in predictions if p.is_fraud),
        total_alerts=total_alerts,
        latency_ms=round(latency_ms, 2),
    )
