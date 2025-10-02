from .engine_base import EngineBase

import random
from .engine_base import EngineBase

class MarketTypeEngine(EngineBase):
    def score(self, context):
        # Example: Score based on market type
        mtype = context.get("market_type", "range")
        score = 1.0 if mtype == "trend" else 0.3
        return score, {"reason": f"market_type={mtype}"}
    def heartbeat(self, scenario=None, context=None):
        return {"calls": 1, "nonzero_ratio": 1.0, "latency_ms": random.randint(1, 5)}
