# Canary scenarios for engine health
from typing import List, Dict

CANARY_SCENARIOS = [
    {"name": "rate_hike_shock", "description": "Simulate sudden rate hike"},
    {"name": "oil_spike", "description": "Simulate oil price spike"},
    {"name": "risk_off", "description": "Simulate risk-off scenario"},
]

def run_canaries(engines: List, context: Dict):
    # Run all canary scenarios
    for scenario in CANARY_SCENARIOS:
        for engine in engines:
            engine.heartbeat(scenario, context)
