from src.core.decision_record import DecisionRecord

def test_supervisor_decision():
    record = DecisionRecord(
        engine_scores={"news": 0.7, "tech": 0.5},
        weights={"news": 0.5, "tech": 0.5},
        gates={"risk": True, "spread": True},
        final_action="buy",
        reasons={"news": "positive", "tech": "bullish"},
        data_age_ms=100
    )
    assert record.final_action in ("buy", "sell", "hold")
    assert all(isinstance(v, float) for v in record.engine_scores.values())
