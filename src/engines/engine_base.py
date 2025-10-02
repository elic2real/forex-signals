# Engine interface for all analysis engines
from typing import Any, Dict, Tuple

class EngineBase:
    def init(self):
        pass
    def score(self, context: Dict[str, Any]) -> Tuple[float, Dict]:
        raise NotImplementedError
    def heartbeat(self, scenario=None, context=None):
        return {"calls": 1, "nonzero_ratio": 1.0, "latency_ms": 0}
