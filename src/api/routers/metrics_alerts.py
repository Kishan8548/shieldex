"""
FastAPI routers — metrics and alerts endpoints.
"""

import json
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from src.api.schemas import MetricsResponse, SpikeAlertResponse, MerchantStatsResponse
from src.api.state import get_app_state

logger = logging.getLogger(__name__)

metrics_router = APIRouter(prefix="/api/v1", tags=["Metrics"])
alerts_router = APIRouter(prefix="/api/v1", tags=["Alerts"])

RESULTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "results"


# ─────────────────────────────────────────────────────────────────────────────
# Metrics endpoints
# ─────────────────────────────────────────────────────────────────────────────

@metrics_router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Get evaluation metrics",
    description="Returns the frozen held-out test set evaluation metrics including PR-AUC, cost analysis, and baseline comparisons.",
)
async def get_metrics():
    state = get_app_state()
    if state.test_metrics is None:
        raise HTTPException(
            status_code=404,
            detail="No evaluation metrics found. Run `python scripts/evaluate.py` first."
        )
    return MetricsResponse(**state.test_metrics)


@metrics_router.get(
    "/metrics/pr-curve",
    summary="Get PR curve data",
    description="Returns precision-recall curve data for the dashboard chart.",
)
async def get_pr_curve():
    pr_curve_path = RESULTS_DIR / "test_pr_curve.json"
    if not pr_curve_path.exists():
        raise HTTPException(status_code=404, detail="PR curve data not found.")
    with open(pr_curve_path) as f:
        return json.load(f)


@metrics_router.get(
    "/metrics/cost-sweep",
    summary="Get cost vs threshold sweep",
    description="Returns the full threshold sweep data for the cost analysis chart.",
)
async def get_cost_sweep():
    cost_path = RESULTS_DIR / "validation_cost_analysis.json"
    if not cost_path.exists():
        raise HTTPException(status_code=404, detail="Cost sweep data not found.")
    with open(cost_path) as f:
        data = json.load(f)
    return data


# ─────────────────────────────────────────────────────────────────────────────
# Alerts endpoints
# ─────────────────────────────────────────────────────────────────────────────

@alerts_router.get(
    "/alerts",
    response_model=list[SpikeAlertResponse],
    summary="Get active spike alerts",
    description="Returns all currently active fraud spike alerts across all merchants.",
)
async def get_active_alerts():
    state = get_app_state()
    alerts = state.spike_detector.get_all_active_alerts()
    return [SpikeAlertResponse(**a) for a in alerts]


@alerts_router.get(
    "/alerts/history",
    response_model=list[SpikeAlertResponse],
    summary="Get alert history",
    description="Returns the last 100 fired spike alerts (resolved and active).",
)
async def get_alert_history():
    state = get_app_state()
    history = state.spike_detector.get_alert_history(limit=100)
    return [SpikeAlertResponse(**a) for a in history]


@alerts_router.get(
    "/merchants",
    response_model=list[MerchantStatsResponse],
    summary="Get all merchant stats",
    description="Returns EWMA fraud rate statistics for all merchants.",
)
async def get_all_merchants():
    state = get_app_state()
    stats = state.spike_detector.get_all_merchant_stats()
    return [MerchantStatsResponse(**s) for s in stats if "ewma_mean" in s]


@alerts_router.get(
    "/merchants/{merchant_id}/stats",
    response_model=MerchantStatsResponse,
    summary="Get per-merchant stats",
    description="Returns EWMA statistics for a specific merchant.",
)
async def get_merchant_stats(merchant_id: str):
    state = get_app_state()
    stats = state.spike_detector.get_merchant_stats(merchant_id)
    if "ewma_mean" not in stats:
        raise HTTPException(status_code=404, detail=f"No data for merchant {merchant_id}")
    return MerchantStatsResponse(**stats)
