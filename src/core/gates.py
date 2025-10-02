# Trading gates: spread, session, news, exposure, drawdown, probability
from decimal import Decimal
from typing import Dict, Any

def check_spread(spread: Decimal, max_spread: Decimal) -> bool:
    return spread <= max_spread

def check_session(session: str, allowed_sessions: list) -> bool:
    return session in allowed_sessions

def check_probability(prob: float, min_prob: float) -> bool:
    return prob >= min_prob


def check_drawdown(nav: float, peak_nav: float, max_dd: float = 0.05) -> bool:
    # True if within drawdown cap
    dd = (peak_nav - nav) / peak_nav if peak_nav > 0 else 0
    return dd <= max_dd

def check_profit_giveback(nav: float, peak_nav: float, giveback_pct: float = 0.3) -> bool:
    # True if profit giveback not exceeded
    profit = peak_nav - nav
    return profit <= (peak_nav * giveback_pct)

def check_loss_streak(losses: int, max_streak: int = 3) -> bool:
    # True if not in cool-off
    return losses < max_streak

def check_kill_switch(nav: float, equity_floor: float) -> bool:
    # True if above equity floor
    return nav >= equity_floor

def log_block(reason: str, details: Dict[str, Any]):
    # Structured log for gate block
    print({"gate_block": reason, **details})
