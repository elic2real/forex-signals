from .engine_base import EngineBase

import random
from .engine_base import EngineBase

class JournalContextEngine(EngineBase):
    def score(self, context):
        # Example: Score based on journal context
        last_entry = context.get("last_journal_entry", "")
        score = 1.0 if "win" in last_entry else 0.2
        return score, {"reason": f"last_entry={last_entry}"}
    def heartbeat(self, scenario=None, context=None):
        return {"calls": 1, "nonzero_ratio": 1.0, "latency_ms": random.randint(1, 5)}
