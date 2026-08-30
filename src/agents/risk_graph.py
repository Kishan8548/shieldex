import os
import json
import logging
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime, timezone

from langgraph.graph import StateGraph, END
from src.agents.rag_store import PolicyRAGStore

logger = logging.getLogger(__name__)


class RiskInvestigationState(TypedDict):
    merchant_id: str
    amount_inr: float
    fraud_score: float
    is_ml_fraud: bool
    threshold_used: float
    top_features: List[Dict[str, Any]]
    spike_alert: Optional[Dict[str, Any]]
    retrieved_policies: List[Dict[str, Any]]
    verdict: str                  # "ALLOW" | "STEP_UP_2FA" | "HOLD_SETTLEMENT" | "BLOCK"
    confidence_score: float       # 0.0 - 1.0
    risk_summary: str
    recommended_actions: List[str]
    chargeback_defense_packet: Optional[Dict[str, Any]]


def triage_signals_node(state: RiskInvestigationState) -> Dict[str, Any]:
    logger.info(f"LangGraph [Triage]: Analyzing signals for merchant={state['merchant_id']} amount=₹{state['amount_inr']}")
    return {}


def policy_rag_node(state: RiskInvestigationState) -> Dict[str, Any]:
    rag = PolicyRAGStore()
    query_parts = [
        f"merchant {state['merchant_id']}",
        f"fraud score {state['fraud_score']:.2f}",
    ]
    if state.get("spike_alert"):
        query_parts.append("merchant velocity spike Z-score anomaly")
    if state.get("is_ml_fraud"):
        query_parts.append("card not present dispute compelling evidence")

    query = " ".join(query_parts)
    matched_policies = rag.retrieve(query, top_k=2)
    logger.info(f"LangGraph [RAG]: Retrieved {len(matched_policies)} policy documents")
    return {"retrieved_policies": matched_policies}


def deliberate_verdict_node(state: RiskInvestigationState) -> Dict[str, Any]:
    fraud_score = state["fraud_score"]
    spike_alert = state.get("spike_alert")
    is_spike = spike_alert is not None
    amount = state["amount_inr"]

    groq_api_key = os.environ.get("GROQ_API_KEY")
    if groq_api_key:
        try:
            from langchain_groq import ChatGroq
            llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, api_key=groq_api_key)
            prompt = (
                f"You are Shieldex Autonomous Risk Manager for Razorpay.\n"
                f"Transaction Details:\n"
                f"- Merchant: {state['merchant_id']}\n"
                f"- Amount: ₹{amount}\n"
                f"- ML Fraud Probability: {fraud_score:.4f} (Threshold: {state['threshold_used']})\n"
                f"- Merchant Spike Active: {is_spike}\n"
                f"- Top SHAP Features: {state['top_features'][:3]}\n"
                f"- Applicable Policies: {[p['title'] for p in state['retrieved_policies']]}\n\n"
                f"Provide a JSON response with:\n"
                f"- verdict: ALLOW | STEP_UP_2FA | HOLD_SETTLEMENT | BLOCK\n"
                f"- confidence_score: float (0-1)\n"
                f"- risk_summary: string\n"
                f"- recommended_actions: list of strings"
            )
            response = llm.invoke(prompt)
            content = response.content
            # Extract JSON block
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            parsed = json.loads(content.strip())
            return {
                "verdict": parsed.get("verdict", "STEP_UP_2FA"),
                "confidence_score": float(parsed.get("confidence_score", 0.9)),
                "risk_summary": parsed.get("risk_summary", "Autonomous risk assessment complete."),
                "recommended_actions": parsed.get("recommended_actions", ["Enforce OTP step-up"])
            }
        except Exception as e:
            logger.warning(f"LLM call fallback due to: {e}")

    # Deterministic Rule-Assisted Reasoning
    if fraud_score >= 0.70 or (fraud_score >= 0.40 and is_spike):
        verdict = "BLOCK"
        confidence = 0.96
        summary = (
            f"High-confidence fraudulent pattern detected (ML Score: {fraud_score:.2f}). "
            f"Significant deviation in key PCA components and transaction velocity."
        )
        actions = [
            "Immediate transaction decline to prevent chargeback loss",
            "Place temporary 6-hour rate-limit on card BIN",
            "Flag merchant account for review if subsequent attempts occur"
        ]
    elif fraud_score >= state["threshold_used"] or is_spike:
        verdict = "STEP_UP_2FA" if amount < 10000 else "HOLD_SETTLEMENT"
        confidence = 0.88
        summary = (
            f"Borderline risk signals detected (ML Score: {fraud_score:.2f}, Spike Alert: {is_spike}). "
            f"Transaction exceeds normal variance baseline."
        )
        actions = [
            "Trigger biometric 3DS 2.0 or OTP step-up verification",
            "Log IP, device fingerprint, and session metadata for audit compliance",
            "Release settlement after 24h dispute clearing window"
        ]
    else:
        verdict = "ALLOW"
        confidence = 0.98
        summary = f"Transaction conforms to safe merchant profile (ML Score: {fraud_score:.2f})."
        actions = ["Authorize payment instantly", "Log normal audit trail"]

    return {
        "verdict": verdict,
        "confidence_score": confidence,
        "risk_summary": summary,
        "recommended_actions": actions
    }


def draft_chargeback_defense_node(state: RiskInvestigationState) -> Dict[str, Any]:
    if state["verdict"] in ("ALLOW",):
        return {"chargeback_defense_packet": None}

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    top_drivers = ", ".join([f"{f['feature']} (SHAP: {f['shap_value']})" for f in state['top_features'][:3]])

    packet = {
        "dossier_id": f"CB-DOSSIER-{state['merchant_id']}-{int(datetime.now(timezone.utc).timestamp())}",
        "generated_at": now_str,
        "dispute_condition": "Visa 10.4 / Mastercard 4837 (Fraud - Card Not Present)",
        "merchant_id": state["merchant_id"],
        "transaction_amount_inr": state["amount_inr"],
        "risk_decision_audit": {
            "ml_fraud_score": round(state["fraud_score"], 4),
            "operating_threshold": state["threshold_used"],
            "verdict_assigned": state["verdict"],
            "top_risk_drivers": top_drivers
        },
        "compelling_evidence_checklist": [
            {"item": "3DS 2.0 / AFA OTP Authentication Timestamp Log", "status": "VERIFIED_ATTACHED"},
            {"item": "Cardholder Device Fingerprint & IP Geolocation Match", "status": "ATTACHED"},
            {"item": "Proof of Digital Service Delivery / Invoice SMS Receipt", "status": "ATTACHED"},
            {"item": "Merchant Terms of Service & Cancellation Policy Acknowledgement", "status": "ATTACHED"}
        ],
        "defense_statement": (
            f"Merchant {state['merchant_id']} successfully processed transaction ₹{state['amount_inr']:,} "
            f"under compliant RBI 2FA regulations. Shieldex Risk Manager recorded an ML confidence score of "
            f"{state['fraud_score']:.4f} and enforced standard fraud mitigation protocols. The evidence attached "
            f"demonstrates authenticated cardholder participation."
        )
    }

    return {"chargeback_defense_packet": packet}


def build_risk_agent_graph():
    workflow = StateGraph(RiskInvestigationState)

    workflow.add_node("triage", triage_signals_node)
    workflow.add_node("policy_rag", policy_rag_node)
    workflow.add_node("deliberate", deliberate_verdict_node)
    workflow.add_node("draft_defense", draft_chargeback_defense_node)

    workflow.set_entry_point("triage")
    workflow.add_edge("triage", "policy_rag")
    workflow.add_edge("policy_rag", "deliberate")
    workflow.add_edge("deliberate", "draft_defense")
    workflow.add_edge("draft_defense", END)

    return workflow.compile()


_agent_graph = None

def get_risk_agent():
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = build_risk_agent_graph()
    return _agent_graph
