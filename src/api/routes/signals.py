from fastapi import APIRouter
from ..models import Signal

router = APIRouter()

@router.get("/signals/active", response_model=Signal)
def get_active_signal():
    # TODO: Return current active signal
    return Signal(
        instrument="EUR_USD",
        signal_type="buy",
        confidence=0.85,
        reasons={"supervisor": "stub"},
        timestamp=0
    )
