import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from src.services.signal_engine import SignalEngine
from src.services.oanda_client import OandaClient
from src.services.fcm_service import FCMService

@pytest.mark.asyncio
async def test_signal_engine_initialization():
    """Test signal engine can be initialized"""
    
    # Mock dependencies
    oanda_client = Mock(spec=OandaClient)
    fcm_service = Mock(spec=FCMService)
    
    # Mock config
    config = Mock()
    config.instruments = ["EUR_USD"]
    config.poll_interval = 1
    config.strategies = {"main_trend_following": {"sl_pips": 15}}
    config.filters = {"max_spread_pips": 2.0}
    
    # Create signal engine
    engine = SignalEngine(oanda_client, fcm_service, config)
    
    assert engine.oanda_client == oanda_client
    assert engine.fcm_service == fcm_service
    assert engine.config == config
    assert not engine.monitoring
    assert len(engine.device_tokens) == 0

@pytest.mark.asyncio 
async def test_device_registration():
    """Test device token registration"""
    
    # Setup
    oanda_client = Mock(spec=OandaClient)
    fcm_service = Mock(spec=FCMService)
    config = Mock()
    
    engine = SignalEngine(oanda_client, fcm_service, config)
    
    # Test registration
    test_token = "test_device_token_123"
    engine.register_device(test_token)
    
    assert test_token in engine.device_tokens
    assert len(engine.device_tokens) == 1
    
    # Test duplicate registration
    engine.register_device(test_token)
    assert len(engine.device_tokens) == 1  # Should not duplicate
    
    # Test unregistration
    engine.unregister_device(test_token)
    assert test_token not in engine.device_tokens
    assert len(engine.device_tokens) == 0

@pytest.mark.asyncio
async def test_oanda_client_price_fetch():
    """Test OANDA client price fetching"""
    
    # Mock OANDA API response
    mock_client = Mock()
    mock_response = {
        "prices": [{
            "closeoutBid": "1.1000",
            "closeoutAsk": "1.1002"
        }]
    }
    mock_client.request.return_value = mock_response
    
    # Create OANDA client
    oanda_client = OandaClient("test_key", "test_account", "practice")
    oanda_client.client = mock_client
    
    # Test price fetch
    price = await oanda_client.get_current_price("EUR_USD")
    
    assert price == 1.1000
    assert mock_client.request.called
