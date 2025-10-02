# Readiness score for trading enablement
from typing import Dict, Any


def compute_readiness(metrics: Dict[str, Any]) -> float:
    # Compute readiness score from metrics
    score = min(1.0, max(0.0, metrics.get("freshness", 1.0)))
    return score

def output_hourly_readiness(metrics: Dict[str, Any]):
    from .logging import log_metric
    score = compute_readiness(metrics)
    log_metric("readiness_score", score)
    print({"readiness_score": score, "metrics": metrics})
