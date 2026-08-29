import pytest
import numpy as np
from src.models.spike_detector import SpikeDetector


class TestSpikeDetector:

    def setup_method(self):
        self.detector = SpikeDetector(alpha=0.15, z_threshold=3.0, min_observations=20)

    def test_no_alert_during_warmup(self):
        for i in range(19):
            alert = self.detector.update("MERCH_001", 0.9)
            assert alert is None

    def test_no_alert_for_stable_baseline(self):
        for _ in range(100):
            self.detector.update("MERCH_001", 0.05)
        for _ in range(50):
            alert = self.detector.update("MERCH_001", 0.06)
            assert alert is None

    def test_fires_alert_on_spike(self):
        for _ in range(100):
            self.detector.update("MERCH_002", 0.03)
        alert = None
        for _ in range(20):
            a = self.detector.update("MERCH_002", 0.95)
            if a is not None:
                alert = a
                break
        assert alert is not None
        assert alert.merchant_id == "MERCH_002"
        assert alert.z_score >= 3.0
        assert alert.severity in ("WARNING", "CRITICAL")

    def test_critical_severity_for_large_spike(self):
        for _ in range(100):
            self.detector.update("MERCH_003", 0.02)
        for _ in range(30):
            a = self.detector.update("MERCH_003", 0.99)
            if a and a.z_score >= 4.5:
                assert a.severity == "CRITICAL"
                return

    def test_alert_auto_resolves(self):
        for _ in range(100):
            self.detector.update("MERCH_004", 0.05)
        for _ in range(5):
            self.detector.update("MERCH_004", 0.95)
        for _ in range(50):
            self.detector.update("MERCH_004", 0.05)
        assert not self.detector.get_merchant_stats("MERCH_004")["has_active_alert"]

    def test_per_merchant_isolation(self):
        for _ in range(100):
            self.detector.update("MERCH_A", 0.05)
            self.detector.update("MERCH_B", 0.05)
        for _ in range(20):
            self.detector.update("MERCH_A", 0.95)
        assert not self.detector.get_merchant_stats("MERCH_B")["has_active_alert"]

    def test_merchant_stats_fields(self):
        self.detector.update("MERCH_STAT", 0.1)
        stats = self.detector.get_merchant_stats("MERCH_STAT")
        assert all(k in stats for k in ["merchant_id", "ewma_mean", "ewma_stddev",
                                         "n_observations", "has_active_alert"])

    def test_unknown_merchant(self):
        assert self.detector.get_merchant_stats("UNKNOWN")["status"] == "no_data"

    def test_ewma_mean_converges(self):
        for _ in range(500):
            self.detector.update("CONV", 0.2)
        stats = self.detector.get_merchant_stats("CONV")
        assert abs(stats["ewma_mean"] - 0.2) < 0.02

    def test_reset_clears_state(self):
        self.detector.update("MERCH_RESET", 0.5)
        self.detector.reset_all()
        assert self.detector.get_merchant_stats("MERCH_RESET")["status"] == "no_data"
