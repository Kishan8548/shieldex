"""Unit tests for cost evaluator — threshold optimization and ₹ cost computation."""

import pytest
import numpy as np
from src.models.cost_evaluator import compute_cost_at_threshold, find_optimal_threshold


class TestCostEvaluator:

    def setup_method(self):
        """Create a simple synthetic y_true and y_prob for testing."""
        rng = np.random.default_rng(42)
        n = 1000
        y_true = np.zeros(n, dtype=int)
        y_true[:50] = 1  # 5% fraud

        # Fraud transactions get higher fraud scores
        y_prob = np.where(y_true == 1, rng.uniform(0.6, 1.0, n), rng.uniform(0.0, 0.4, n))
        self.y_true = y_true
        self.y_prob = y_prob

    def test_compute_cost_at_threshold_zero(self):
        """At threshold=0, everything is flagged — all FP, no FN."""
        result = compute_cost_at_threshold(self.y_true, self.y_prob, threshold=0.0)
        assert result["FN"] == 0, "At threshold=0, should catch all fraud (no FN)"
        assert result["cost_fn_inr"] == 0

    def test_compute_cost_at_threshold_one(self):
        """At threshold=1, nothing is flagged — all FN, no FP."""
        result = compute_cost_at_threshold(self.y_true, self.y_prob, threshold=1.0)
        assert result["FP"] == 0, "At threshold=1, should not block anything (no FP)"
        assert result["cost_fp_inr"] == 0

    def test_cost_components_sum_correctly(self):
        """Total cost should equal FN * cost_fn + FP * cost_fp."""
        cost_fn, cost_fp = 5000, 150
        result = compute_cost_at_threshold(self.y_true, self.y_prob, 0.5, cost_fn, cost_fp)
        expected = result["FN"] * cost_fn + result["FP"] * cost_fp
        assert result["total_cost_inr"] == expected

    def test_precision_recall_in_bounds(self):
        """Precision and recall must be in [0, 1]."""
        for threshold in [0.1, 0.3, 0.5, 0.7, 0.9]:
            result = compute_cost_at_threshold(self.y_true, self.y_prob, threshold)
            assert 0.0 <= result["precision"] <= 1.0
            assert 0.0 <= result["recall"] <= 1.0

    def test_confusion_matrix_sums_to_n(self):
        """TP + FP + TN + FN should equal total samples."""
        n = len(self.y_true)
        result = compute_cost_at_threshold(self.y_true, self.y_prob, 0.5)
        total = result["TP"] + result["FP"] + result["TN"] + result["FN"]
        assert total == n

    def test_optimal_threshold_lower_than_extremes(self):
        """Optimal threshold cost should be lower than flag-all and flag-none."""
        report = find_optimal_threshold(self.y_true, self.y_prob)
        opt_cost = report["optimal_metrics"]["total_cost_inr"]
        flag_none = report["baselines"]["flag_nothing"]["total_cost_inr"]
        flag_all = report["baselines"]["flag_everything"]["total_cost_inr"]
        assert opt_cost <= flag_none, "Optimal cost should be <= flag-nothing cost"
        assert opt_cost <= flag_all, "Optimal cost should be <= flag-everything cost"

    def test_optimal_threshold_in_valid_range(self):
        """Optimal threshold should be between 0.01 and 0.99."""
        report = find_optimal_threshold(self.y_true, self.y_prob)
        threshold = report["optimal_threshold"]
        assert 0.01 <= threshold <= 0.99

    def test_cost_savings_are_positive(self):
        """Cost savings vs naive baselines should be non-negative."""
        report = find_optimal_threshold(self.y_true, self.y_prob)
        assert report["cost_savings_vs_flag_nothing_inr"] >= 0
        # Note: savings vs flag_everything might be negative in some edge cases

    def test_pr_auc_present_in_generate_report(self, tmp_path):
        """generate_cost_report should include PR-AUC."""
        from src.models.cost_evaluator import generate_cost_report
        result = generate_cost_report(self.y_true, self.y_prob, label="test", save=False)
        assert "pr_auc" in result
        assert 0.0 <= result["pr_auc"] <= 1.0

    def test_full_sweep_covers_range(self):
        """Full threshold sweep should have data points across the range."""
        report = find_optimal_threshold(self.y_true, self.y_prob, n_thresholds=100)
        sweep = report["full_threshold_sweep"]
        assert len(sweep) == 100
        thresholds = [r["threshold"] for r in sweep]
        assert min(thresholds) <= 0.05
        assert max(thresholds) >= 0.95
