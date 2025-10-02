# Pydantic models for API contracts
from pydantic import BaseModel
from typing import Dict, Any

class Signal(BaseModel):
    instrument: str
    signal_type: str
    confidence: float
    reasons: Dict[str, Any]
    timestamp: int

class Trade(BaseModel):
    instrument: str
    units: float
    side: str
    price: float
    timestamp: int

class JournalEntry(BaseModel):
    entry: str
    context: Dict[str, Any]
    timestamp: int
