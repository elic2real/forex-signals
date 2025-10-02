# Engine heartbeat and stats
from typing import Dict, Any

def record_heartbeat(engine_name: str, stats: Dict[str, Any]):
    # Log heartbeat stats
    print({"engine": engine_name, **stats})
