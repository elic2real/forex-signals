from fastapi import APIRouter
from ..models import Trade

router = APIRouter()

@router.get("/trades", response_model=Trade)
def get_trade():
    # TODO: Return trade info
    return Trade(
        instrument="EUR_USD",
        units=1000,
        side="buy",
        price=1.1000,
        timestamp=0
    )
