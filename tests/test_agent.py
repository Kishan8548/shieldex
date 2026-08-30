import pytest
from src.agents.rag_store import PolicyRAGStore
from src.agents.risk_graph import get_risk_agent


def test_rag_store_retrieval():
    rag = PolicyRAGStore()
    docs = rag.retrieve("Mastercard reason code card not present dispute", top_k=2)
    assert len(docs) == 2
    assert any("VISA" in d["id"] or "MASTERCARD" in d["id"] for d in docs)


def test_langgraph_agent_benign_transaction():
    agent = get_risk_agent()
    state = {
        "merchant_id": "MERCH_TEST",
        "amount_inr": 1200.0,
        "fraud_score": 0.04,
        "is_ml_fraud": False,
        "threshold_used": 0.3596,
        "top_features": [{"feature": "Amount", "shap_value": 0.01}],
        "spike_alert": None,
        "retrieved_policies": [],
        "verdict": "",
        "confidence_score": 0.0,
        "risk_summary": "",
        "recommended_actions": [],
        "chargeback_defense_packet": None,
    }

    result = agent.invoke(state)
    assert result["verdict"] == "ALLOW"
    assert result["confidence_score"] > 0.9
    assert len(result["retrieved_policies"]) > 0
    assert result["chargeback_defense_packet"] is None


def test_langgraph_agent_fraud_spike_transaction():
    agent = get_risk_agent()
    state = {
        "merchant_id": "MERCH_HIGH_RISK",
        "amount_inr": 48500.0,
        "fraud_score": 0.89,
        "is_ml_fraud": True,
        "threshold_used": 0.3596,
        "top_features": [
            {"feature": "V14", "shap_value": 0.45},
            {"feature": "V4", "shap_value": 0.32},
            {"feature": "Amount", "shap_value": 0.28},
        ],
        "spike_alert": {"severity": "CRITICAL", "z_score": 6.8},
        "retrieved_policies": [],
        "verdict": "",
        "confidence_score": 0.0,
        "risk_summary": "",
        "recommended_actions": [],
        "chargeback_defense_packet": None,
    }

    result = agent.invoke(state)
    assert result["verdict"] == "BLOCK"
    assert len(result["recommended_actions"]) > 0
    assert result["chargeback_defense_packet"] is not None
    assert result["chargeback_defense_packet"]["merchant_id"] == "MERCH_HIGH_RISK"
    assert "compelling_evidence_checklist" in result["chargeback_defense_packet"]
