from .engine_base import EngineBase

import random
from .engine_base import EngineBase

class FundamentalEngine(EngineBase):
    def score(self, context):
        # Example: Score based on fundamental news
        news_score = context.get("fundamental_news_score", 0.0)
        score = min(1.0, max(0.0, news_score))
        return score, {"reason": f"news_score={news_score}"}
    def heartbeat(self, scenario=None, context=None):
        return {"calls": 1, "nonzero_ratio": 1.0, "latency_ms": random.randint(1, 5)}
