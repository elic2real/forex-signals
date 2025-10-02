import pytest
from decimal import Decimal
from src.core import risk_math, house_money
from src.adapters.oanda_adapter import OandaAdapter
from src.adapters.firebase_adapter import FirebaseAdapter
# Property-based testing
from hypothesis import given, strategies as st

def test_pip_value_precision():
    # JPY pairs
    assert risk_math.pip_value('USDJPY', Decimal('1000'), Decimal('110')) == Decimal('1000') * Decimal('0.01') * Decimal('110')
    # Non-JPY pairs
    assert risk_math.pip_value('EURUSD', Decimal('1000'), Decimal('1.1')) == Decimal('1000') * Decimal('0.0001') * Decimal('1.1')

@given(
    units=st.decimals(min_value=1, max_value=1_000_000, allow_nan=False, allow_infinity=False),
    price=st.decimals(min_value=0.01, max_value=200, allow_nan=False, allow_infinity=False)
)
def test_pip_value_property(units, price):
    # JPY pairs
    pip_jpy = risk_math.pip_value('USDJPY', units, price)
    assert pip_jpy == units * Decimal('0.01') * price
    # Non-JPY pairs
    pip_non_jpy = risk_math.pip_value('EURUSD', units, price)
    assert pip_non_jpy == units * Decimal('0.0001') * price

def test_house_money_breakpoints(sample_nav):
    # Placeholder: always returns nav
    assert house_money.compute(sample_nav, Decimal('0.0')) == sample_nav

def test_oanda_adapter_contract(oanda_order):
    adapter = OandaAdapter(api_key='test', account_id='test')
    result = adapter.place_order(oanda_order)
    assert isinstance(result, dict)
    assert 'status' in result

def test_firebase_adapter_contract(firebase_entry):
    adapter = FirebaseAdapter(service_account_path='dummy.json')
    # Should not raise
    adapter.send_journal(firebase_entry)
    adapter.send_signal_alert(firebase_entry)
