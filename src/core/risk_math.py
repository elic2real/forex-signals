# Core risk math utilities for pip, R, and unit calculations
from decimal import Decimal

def pip_value(pair: str, units: Decimal, price: Decimal) -> Decimal:
    # JPY pairs: pip = 0.01, others: 0.0001
    pip = Decimal('0.01') if 'JPY' in pair else Decimal('0.0001')
    return units * pip * price

def golden_tests():
    # Add golden tests for pip value, R, etc.
    pass
