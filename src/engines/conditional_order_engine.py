from .engine_base import EngineBase

import random
from .engine_base import EngineBase

class ConditionalOrderEngine(EngineBase):
    def score(self, context):
        # Example: Score based on presence of a conditional trigger
        trigger = context.get("conditional_trigger", False)
        score = 1.0 if trigger else 0.1
        return score, {"reason": "conditional_trigger" if trigger else "no_trigger"}
    def heartbeat(self, scenario=None, context=None):
        return {"calls": 1, "nonzero_ratio": 1.0, "latency_ms": random.randint(1, 5)}
