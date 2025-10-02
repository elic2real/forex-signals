from .engine_base import EngineBase

import random
from .engine_base import EngineBase

class VolumeVelocityEngine(EngineBase):
    def score(self, context):
        # Example: Score based on volume and velocity
        volume = context.get("volume", 1000)
        velocity = context.get("velocity", 1.0)
        score = min(1.0, (volume / 10000) * velocity)
        return score, {"reason": f"volume={volume},velocity={velocity}"}
    def heartbeat(self, scenario=None, context=None):
        return {"calls": 1, "nonzero_ratio": 1.0, "latency_ms": random.randint(1, 5)}
