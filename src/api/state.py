import logging
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"
RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "results"


@dataclass
class AppState:
    ensemble: Optional[object] = None
    scaler: Optional[object] = None
    spike_detector: Optional[object] = None
    test_metrics: Optional[dict] = None
    is_ready: bool = False


_state = AppState()


def get_app_state() -> AppState:
    return _state


def load_models():
    global _state
    logger.info("Loading models...")
    try:
        from src.models.classifier import FraudEnsemble
        from src.data.preprocessor import load_scaler
        from src.models.spike_detector import SpikeDetector

        _state.ensemble = FraudEnsemble.load(MODELS_DIR)
        _state.scaler = load_scaler(MODELS_DIR)
        _state.spike_detector = SpikeDetector(alpha=0.15, z_threshold=3.0, min_observations=20)

        metrics_path = RESULTS_DIR / "test_metrics.json"
        pr_curve_path = RESULTS_DIR / "test_pr_curve.json"
        if metrics_path.exists():
            with open(metrics_path) as f:
                _state.test_metrics = json.load(f)
            if pr_curve_path.exists():
                with open(pr_curve_path) as f:
                    _state.test_metrics["pr_curve"] = json.load(f)

        _state.is_ready = True
        logger.info("Models loaded. API ready.")
    except FileNotFoundError as e:
        logger.error(f"Model files not found: {e}. Run scripts/train.py first.")
        _state.is_ready = False
    except Exception as e:
        logger.error(f"Failed to load models: {e}", exc_info=True)
        _state.is_ready = False
