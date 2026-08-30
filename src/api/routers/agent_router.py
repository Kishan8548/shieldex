import time
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.agents.risk_graph import get_risk_agent
from src.agents.rag_store import PolicyRAGStore
from src.api.state import get_app_state

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/agent", tags=["AI Risk Agent"])


class AgentInvestigationRequest(BaseModel):
    merchant_id: str
    amount_inr: float = Field(..., ge=0)
    fraud_score: float = Field(..., ge=0, le=1)
    is_ml_fraud: bool
    threshold_used: float = 0.3596
    top_features: List[Dict[str, Any]] = []
    spike_alert: Optional[Dict[str, Any]] = None


class AgentInvestigationResponse(BaseModel):
    merchant_id: str
    amount_inr: float
    fraud_score: float
    verdict: str
    confidence_score: float
    risk_summary: str
    recommended_actions: List[str]
    retrieved_policies: List[Dict[str, Any]]
    chargeback_defense_packet: Optional[Dict[str, Any]] = None
    execution_time_ms: float


class ChargebackDraftRequest(BaseModel):
    merchant_id: str
    amount_inr: float
    fraud_score: float
    dispute_condition: Optional[str] = "Visa 10.4 / Mastercard 4837 (Fraud - Card Not Present)"
    top_features: List[Dict[str, Any]] = []


@router.post(
    "/investigate",
    response_model=AgentInvestigationResponse,
    summary="Run Autonomous LangGraph Risk Investigation",
    description=(
        "Executes a multi-node LangGraph agent workflow: triages ML and EWMA signals, "
        "retrieves RBI / Razorpay regulatory guidelines via RAG, deliberates an autonomous verdict, "
        "and drafts a chargeback defense packet if required."
    ),
)
async def investigate_transaction(request: AgentInvestigationRequest):
    start = time.perf_counter()
    agent = get_risk_agent()

    initial_state = {
        "merchant_id": request.merchant_id,
        "amount_inr": request.amount_inr,
        "fraud_score": request.fraud_score,
        "is_ml_fraud": request.is_ml_fraud,
        "threshold_used": request.threshold_used,
        "top_features": request.top_features,
        "spike_alert": request.spike_alert,
        "retrieved_policies": [],
        "verdict": "",
        "confidence_score": 0.0,
        "risk_summary": "",
        "recommended_actions": [],
        "chargeback_defense_packet": None,
    }

    try:
        final_state = agent.invoke(initial_state)
        latency_ms = (time.perf_counter() - start) * 1000

        return AgentInvestigationResponse(
            merchant_id=final_state["merchant_id"],
            amount_inr=final_state["amount_inr"],
            fraud_score=final_state["fraud_score"],
            verdict=final_state["verdict"],
            confidence_score=round(final_state["confidence_score"], 3),
            risk_summary=final_state["risk_summary"],
            recommended_actions=final_state["recommended_actions"],
            retrieved_policies=final_state["retrieved_policies"],
            chargeback_defense_packet=final_state.get("chargeback_defense_packet"),
            execution_time_ms=round(latency_ms, 2),
        )
    except Exception as e:
        logger.error(f"Agent investigation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent workflow error: {str(e)}")


@router.get("/policies", summary="Retrieve all RAG policy documents")
async def list_policies():
    rag = PolicyRAGStore()
    return rag.documents
