from .engine_base import EngineBase

class SupervisorEngine(EngineBase):
    def __init__(self, engines, weights):
        self.engines = engines
        self.weights = weights
    def score(self, context):
        # Aggregate engine scores using weights
        scores = {}
        reasons = {}
        for name, engine in self.engines.items():
            score, reason = engine.score(context)
            scores[name] = score
            reasons[name] = reason
        # Weighted sum
        final_score = sum(scores[n] * self.weights.get(n, 1.0) for n in scores)
        return final_score, reasons
