from .engine_base import EngineBase

import random
from .engine_base import EngineBase

class NewsEngine(EngineBase):
    def score(self, context):
        # Example: Score based on news sentiment
        sentiment = context.get("news_sentiment", 0.0)
        score = min(1.0, max(0.0, sentiment))
        return score, {"reason": f"sentiment={sentiment}"}
    def heartbeat(self, scenario=None, context=None):
        return {"calls": 1, "nonzero_ratio": 1.0, "latency_ms": random.randint(1, 5)}
