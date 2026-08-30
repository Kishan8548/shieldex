import re
import math
from typing import List, Dict, Any


DOCUMENTS = [
    {
        "id": "RBI_MANDATE_2FA",
        "category": "Regulatory",
        "title": "RBI Guidelines on Additional Factor of Authentication (AFA)",
        "content": (
            "Under RBI Master Directions on Card Transactions, all domestic Card-Not-Present (CNP) "
            "transactions must enforce Additional Factor of Authentication (2FA/OTP). Transactions "
            "attempting to bypass 2FA or executed via recurring tokenization anomalies must be subjected "
            "to step-up verification or immediate hold if fraud confidence exceeds risk thresholds."
        ),
    },
    {
        "id": "VISA_10_4_DISPUTE",
        "category": "Dispute / Chargeback",
        "title": "Visa Dispute Condition 10.4: Other Fraud in Card-Not-Present Environment",
        "content": (
            "Condition 10.4 applies when cardholder denies authorizing a digital transaction. "
            "Compelling Evidence to overturn: Proof of customer authentication (3DS OTP logs), "
            "IP address matching cardholder location history, proof of digital receipt delivery to verified "
            "mobile/email, device fingerprint consistency, and positive historical transactions from the same account."
        ),
    },
    {
        "id": "MASTERCARD_4837_FRAUD",
        "category": "Dispute / Chargeback",
        "title": "Mastercard Reason Code 4837: No Cardholder Authorization",
        "content": (
            "Merchant defense requires providing verifiable proof of authorization: matched AVS/CVV verification, "
            "timestamped delivery confirmations, device fingerprinting tokens, and customer identity verification. "
            "If transaction amount deviates >300% from merchant average without prior step-up, liability rests on acquirer/merchant."
        ),
    },
    {
        "id": "RAZORPAY_MERCHANT_SPIKE_POLICY",
        "category": "Merchant Risk",
        "title": "Razorpay Merchant Velocity & Risk Spike Protocol",
        "content": (
            "When a merchant's rolling EWMA fraud rate exhibits a Z-Score >= 3.0 (critical spike), the gateway "
            "must trigger automated defensive measures: (1) Enforce mandatory biometric/3DS 2.0 step-up on all incoming "
            "transactions for that merchant, (2) Place high-value payouts on rolling 24-hour settlement hold, (3) Request "
            "merchant verification of recent promotional traffic."
        ),
    },
    {
        "id": "CHARGEBACK_EVIDENCE_REQUIREMENTS",
        "category": "Evidence Generation",
        "title": "Standard Chargeback Defense Evidence Package Standards",
        "content": (
            "A valid dispute response packet must contain: (1) Transaction audit log with UTC timestamp and gateway reference ID, "
            "(2) ML risk evaluation score and reason codes, (3) Customer communication trails, (4) Refund/Cancellation policy disclosure "
            "acknowledged at checkout, and (5) Delivery confirmation or service access logs."
        ),
    },
    {
        "id": "HIGH_VELOCITY_CARD_ATTACK",
        "category": "Attack Pattern",
        "title": "Automated Card Testing & High-Velocity Bot Attacks",
        "content": (
            "Fraud rings use bots to execute micro-transactions to test stolen card viability. Key markers: rapid burst of small "
            "amounts across distinct card bins within minutes, identical device fingerprints, and abnormal merchant fraud spike metrics. "
            "Protocol: Instant IP/Bin block and temporary CAPTCHA enforcement."
        ),
    }
]


class PolicyRAGStore:
    """Lightweight in-memory semantic retriever for payment risk & dispute policies."""

    def __init__(self, documents: List[Dict[str, Any]] = None):
        self.documents = documents or DOCUMENTS
        self.vocabulary = self._build_vocab()

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b[a-z0-9_]{2,}\b", text.lower())

    def _build_vocab(self) -> Dict[str, int]:
        vocab = {}
        for doc in self.documents:
            tokens = self._tokenize(doc["title"] + " " + doc["content"])
            for t in tokens:
                if t not in vocab:
                    vocab[t] = len(vocab)
        return vocab

    def _vectorize(self, text: str) -> Dict[str, float]:
        tokens = self._tokenize(text)
        if not tokens:
            return {}
        counts = {}
        for t in tokens:
            counts[t] = counts.get(t, 0) + 1
        norm = math.sqrt(sum(v * v for v in counts.values())) or 1.0
        return {k: v / norm for k, v in counts.items()}

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        intersection = set(vec1.keys()) & set(vec2.keys())
        return sum(vec1[k] * vec2[k] for k in intersection)

    def retrieve(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        query_vec = self._vectorize(query)
        scored_docs = []

        for doc in self.documents:
            doc_vec = self._vectorize(doc["title"] + " " + doc["content"])
            score = self._cosine_similarity(query_vec, doc_vec)
            scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k]]
