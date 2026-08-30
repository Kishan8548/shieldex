import pytest
from fastapi.testclient import TestClient
from src.api.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        res = client.get("/api/v1/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] in ("healthy", "degraded")
        assert "version" in data


def test_metrics_endpoint():
    with TestClient(app) as client:
        res = client.get("/api/v1/metrics")
        assert res.status_code == 200
        data = res.json()
        assert "pr_auc" in data
        assert "precision" in data
        assert "recall" in data
        assert "model_total_cost_inr" in data


def test_predict_single_endpoint():
    payload = {
        "merchant_id": "MERCH_001",
        "Amount": 120.50,
        "V1": -1.3598, "V2": -0.0728, "V3": 2.5363, "V4": 1.3782, "V5": -0.3383,
        "V6": 0.4624, "V7": 0.2396, "V8": 0.0987, "V9": 0.3638, "V10": 0.0908,
        "V11": -0.5516, "V12": -0.6178, "V13": -0.9914, "V14": -0.3112, "V15": 1.4682,
        "V16": -0.4704, "V17": 0.2080, "V18": 0.0258, "V19": 0.4040, "V20": 0.2514,
        "V21": -0.0183, "V22": 0.2778, "V23": -0.1105, "V24": 0.0669, "V25": 0.1285,
        "V26": -0.1891, "V27": 0.1336, "V28": -0.0211
    }
    with TestClient(app) as client:
        res = client.post("/api/v1/predict", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "fraud_score" in data
        assert "is_fraud" in data
        assert "top_features" in data
        assert "latency_ms" in data


def test_agent_investigate_endpoint():
    payload = {
        "merchant_id": "MERCH_API_TEST",
        "amount_inr": 25000.0,
        "fraud_score": 0.85,
        "is_ml_fraud": True,
        "threshold_used": 0.3596,
        "top_features": [{"feature": "V14", "shap_value": 0.42}],
        "spike_alert": None
    }
    with TestClient(app) as client:
        res = client.post("/api/v1/agent/investigate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["verdict"] in ("ALLOW", "STEP_UP_2FA", "HOLD_SETTLEMENT", "BLOCK")
        assert len(data["recommended_actions"]) > 0
        assert len(data["retrieved_policies"]) > 0


def test_merchants_and_alerts_endpoints():
    with TestClient(app) as client:
        res_m = client.get("/api/v1/merchants")
        assert res_m.status_code == 200
        res_a = client.get("/api/v1/alerts")
        assert res_a.status_code == 200
