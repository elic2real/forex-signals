import pytest
from decimal import Decimal
from src.core import house_money

@pytest.mark.parametrize("nav,day_profit", [
    (Decimal('10000'), Decimal('0.0')),
    (Decimal('10000'), Decimal('0.05')),
    (Decimal('5000'), Decimal('-0.02')),
])
def test_house_money_breakpoints(nav, day_profit):
    # Placeholder: always returns nav
    result = house_money.compute(nav, day_profit)
    assert isinstance(result, Decimal)
    assert result >= 0
