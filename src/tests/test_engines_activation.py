from src.engines.engine_base import EngineBase
import pytest

class DummyEngine(EngineBase):
    def score(self, context):
        return 0.5, {"activated": True}

def test_engine_activation():
    engine = DummyEngine()
    score, meta = engine.score({})
    assert 0 <= score <= 1
    assert meta["activated"] is True
