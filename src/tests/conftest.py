import pytest
from decimal import Decimal

@pytest.fixture
def sample_nav():
    return Decimal('10000')

@pytest.fixture
def sample_day_profit():
    return Decimal('0.02')

@pytest.fixture
def oanda_order():
    return {
        'instrument': 'EURUSD',
        'units': 1000,
        'side': 'buy',
        'type': 'market',
        'price': 1.1000
    }

@pytest.fixture
def firebase_entry():
    return {
        'user_id': 'test_user',
        'action': 'signal',
        'details': {'pair': 'EURUSD', 'signal': 'buy'}
    }
