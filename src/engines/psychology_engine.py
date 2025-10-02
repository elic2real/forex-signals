from .engine_base import EngineBase

import random
from .engine_base import EngineBase

class PsychologyEngine(EngineBase):
    def score(self, context):
        # Example: Score based on trader psychology
        mood = context.get("trader_mood", "neutral")
        score = 1.0 if mood == "confident" else 0.4
        return score, {"reason": f"mood={mood}"}
    def heartbeat(self, scenario=None, context=None):
        return {"calls": 1, "nonzero_ratio": 1.0, "latency_ms": random.randint(1, 5)}
