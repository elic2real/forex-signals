# DecisionRecord structure for every loop
from typing import Dict, Any
from decimal import Decimal

class DecisionRecord:
    def __init__(self, engine_scores: Dict[str, float], weights: Dict[str, float], gates: Dict[str, bool], final_action: str, reasons: Dict[str, Any], data_age_ms: int):
        self.engine_scores = engine_scores
        self.weights = weights
        self.gates = gates
        self.final_action = final_action
        self.reasons = reasons
        self.data_age_ms = data_age_ms
