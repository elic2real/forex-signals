from .engine_base import EngineBase

import random
from .engine_base import EngineBase

class TechnicalEngine(EngineBase):
    def score(self, context):
        # Example: Score based on technical indicator
        rsi = context.get("rsi", 50)
        score = 1.0 if rsi > 70 else (0.0 if rsi < 30 else 0.5)
        return score, {"reason": f"rsi={rsi}"}
    def heartbeat(self, scenario=None, context=None):
        return {"calls": 1, "nonzero_ratio": 1.0, "latency_ms": random.randint(1, 5)}
