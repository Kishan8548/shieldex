# 🛡️ Shieldex — Two-Layer AI Risk Manager

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![LightGBM](https://img.shields.io/badge/LightGBM-4.3.0-brightgreen.svg?style=flat)](https://lightgbm.readthedocs.io/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0.3-orange.svg?style=flat)](https://xgboost.readthedocs.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-RAG%20Agent-blueviolet.svg?style=flat)](https://github.com/langchain-ai/langgraph)
[![Tests](https://img.shields.io/badge/Tests-28%20Passing-success.svg?style=flat)](tests/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat)](LICENSE)

> **Razorpay AI Buildathon — Track 02: AI Risk Manager**  
> *Stop the merchant losing money to fraud, returns, and chargebacks.*  
> **Strictly Defense-Only.** Measured on a 20% stratified held-out test set (56,962 transactions) with honest Indian Rupee (₹) cost-matrix evaluation.

---

## 📌 Architecture Overview

Shieldex implements a three-tier defense architecture engineered for sub-15ms inference latency and deployment on free-tier infrastructure (512MB RAM):

```
                               ┌───────────────────────────────────┐
                               │    Incoming Payment Transaction   │
                               └─────────────────┬─────────────────┘
                                                 │
                                                 ▼
                              ┌─────────────────────────────────────┐
                              │  Layer 1: High-Speed ML Classifier  │
                              │  - LightGBM + XGBoost Soft Ensemble │
                              │  - TreeExplainer SHAP Feature Import│
                              │  - Cost-Optimized Threshold (0.3596)│
                              └──────────────────┬──────────────────┘
                                                 │
                                                 ▼
                              ┌─────────────────────────────────────┐
                              │  Layer 2: EWMA Rate Anomaly Radar   │
                              │  - Rolling Per-Merchant Fraud Mean  │
                              │  - Adaptive Z-Score Anomaly Trigger │
                              │  - 100% Burst Detection in 1.0 Txn  │
                              └──────────────────┬──────────────────┘
                                                 │
                                                 ▼ (On High Risk / Spike Trigger)
                              ┌─────────────────────────────────────┐
                              │  Layer 3: LangGraph RAG Agent       │
                              │  - Node 1: Triage Signals & SHAP    │
                              │  - Node 2: RBI & Visa/MC Policy RAG │
                              │  - Node 3: Autonomous Verdict Synthe│
                              │  - Node 4: Chargeback Dossier Draft │
                              └─────────────────────────────────────┘
```

---

## 📊 Honest Evaluation Metrics (Held-Out Test Set)

Evaluated on **56,962 test transactions** with extreme **0.172% class imbalance** (1 fraud per 577 transactions):

| Metric | Measured Value | Baseline (Logistic Regression) |
|---|---|---|
| **PR-AUC (Target Metric)** | **0.8610** | 0.7104 (+15.1%) |
| **ROC-AUC** | **0.9841** | 0.9420 |
| **Precision** | **88.89%** | 62.40% |
| **Recall** | **81.63%** | 78.50% |
| **F1 Score** | **0.8511** | 0.6950 |
| **Operating Threshold** | **0.3596** *(Cost-Tuned)* | 0.5000 (Naive) |
| **Spike Detection Latency** | **1.0 Transaction** | N/A |
| **Spike False Alarm Rate** | **0.0%** | N/A |

### 💰 ₹ Indian Rupee Cost-Matrix Breakdown

- **False Negative Cost ($C_{FN}$):** ₹5,000 per transaction *(merchant loss / chargeback penalty)*
- **False Positive Cost ($C_{FP}$):** ₹150 per transaction *(customer friction / verification churn)*

$$\text{Total Loss} = FN \times ₹5,000 + FP \times ₹150$$

| Strategy | Total Cost on Test Set | ₹ Saved vs Flag-Nothing |
|---|---|---|
| **Flag Nothing (Naive)** | ₹490,000 | ₹0 |
| **Flag Everything (Naive)** | ₹8,529,600 | -₹8,039,600 |
| **Default 0.50 Threshold** | ₹96,050 | ₹393,950 |
| **Shieldex (Cost-Tuned $\tau = 0.3596$)** | **₹91,500** | **₹398,500** |

---

## 🤖 LangGraph Autonomous Copilot & Policy RAG

When anomalous transactions or merchant bursts occur, Shieldex invokes an autonomous **LangGraph State Graph** backed by an in-memory **Policy RAG Store** containing:
- **RBI Master Directions on Additional Factor of Authentication (AFA/2FA)**
- **Visa Dispute Condition 10.4 (Fraud in Card-Not-Present Environment)**
- **Mastercard Reason Code 4837 (No Cardholder Authorization)**
- **Razorpay Merchant Velocity & Risk Spike Protocols**

The agent deliberates an autonomous verdict (`ALLOW`, `STEP_UP_2FA`, `HOLD_SETTLEMENT`, `BLOCK`) and automatically formats a **Chargeback Defense Dossier** with verifiable compelling evidence checklists (3DS OTP timestamp logs, IP geolocation matches, SMS invoice delivery trails).

---

## ⚡ Quickstart & Local Setup

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/Kishan8548/shieldex.git
cd shieldex

# Install Python backend dependencies
pip install -r requirements.txt

# Install React frontend dependencies
cd frontend && npm install && cd ..
```

### 2. Run Training Pipeline & Test Evaluation
```bash
# 1. Download Kaggle creditcard.csv into data/raw/creditcard.csv
# 2. Run EDA data extraction & Jupyter notebook generation
python scripts/run_eda.py

# 3. Train models and tune hyperparameters via Optuna
python scripts/train.py --n-trials 20

# 4. Run frozen test set evaluation
python scripts/evaluate.py
```

### 3. Run Test Suite (28 Tests)
```bash
pytest tests/ -v
```

### 4. Start Full-Stack App
```bash
# Terminal 1: Start FastAPI Backend (Port 8000)
uvicorn src.api.main:app --reload --port 8000

# Terminal 2: Start React Frontend (Port 3000)
cd frontend && npm run dev
```

Visit `http://localhost:3000` to interact with the 3D parallax landing and live defense operations console.

---

## 🌐 Cloud Production Deployment

Shieldex is lightweight (~140MB RAM footprint) and production-ready for standard containerized or serverless hosting:
- **API Web Service:** FastAPI asynchronous backend (`uvicorn src.api.main:app --workers 4`).
- **UI Web App:** Production static bundle built via `npm run build` in `frontend/dist/`.

---

## 📄 License & Compliance

- **Track:** Razorpay AI Buildathon — Track 02: AI Risk Manager
- **Compliance:** Defense-only. Contains no offensive or evasion capability.
- **License:** MIT
