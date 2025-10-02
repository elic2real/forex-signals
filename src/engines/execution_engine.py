from .engine_base import EngineBase

import random
from .engine_base import EngineBase

class ExecutionEngine(EngineBase):
    def score(self, context):
        # Example: Score based on execution quality
        latency = context.get("execution_latency_ms", 100)
        score = max(0.0, 1.0 - latency / 1000)
        return score, {"reason": f"latency={latency}"}
    def heartbeat(self, scenario=None, context=None):
        return {"calls": 1, "nonzero_ratio": 1.0, "latency_ms": random.randint(1, 5)}
