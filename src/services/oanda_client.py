"""OANDA API client for market data and account information"""

import structlog
from oandapyV20 import API
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.positions as positions
from typing import Dict, List, Optional, Any
import pandas as pd
from .trading_utils import (
    JPY_PIP_SIZE, STANDARD_PIP_SIZE, JPY_PRECISION, STANDARD_PRECISION, 
    MIN_TRADE_SIZE, pip_size_for, oanda_price_precision, oanda_min_trade_size,
    print_once
)
import random
import math

logger = structlog.get_logger()

class OandaClientError(Exception):
    """Custom exception for OANDA client errors"""
    pass

class OandaClientNotInitialized(OandaClientError):
    """Exception raised when OANDA client is not properly initialized"""
    def __init__(self, message: str = "OANDA client not initialized - check API credentials"):
        self.message = message
        super().__init__(self.message)

# Mock trading constants
MOCK_PRICE_VARIANCE = 0.005  # 0.5% price variance for mock data
MOCK_HIGH_VARIANCE_MIN = 0.0001  # Minimum high price variance
MOCK_HIGH_VARIANCE_MAX = 0.003   # Maximum high price variance  
MOCK_LOW_VARIANCE_MIN = 0.0001   # Minimum low price variance
MOCK_LOW_VARIANCE_MAX = 0.003    # Maximum low price variance
MOCK_CLOSE_VARIANCE = 0.002      # Close price variance
MOCK_VOLUME_MIN = 100            # Minimum mock volume
MOCK_VOLUME_MAX = 1000           # Maximum mock volume

class OandaClient:
    def __init__(self, api_key: str, account_id: str, environment: str = "practice"):
        self.api_key = api_key
        self.account_id = account_id
        self.environment = environment
        
        # Production: Default to live environment for production deployment
        # Development: Use practice environment for testing
        if environment == "production":
            self.environment = "live"
        
        # Enable mock mode for test credentials or missing credentials
        self.mock_mode = (
            api_key in ["test_api_key", "", None] or 
            account_id in ["test_account_id", "", None]
        )
        
        if not self.mock_mode:
            if self.environment == "live":
                self.client = API(access_token=api_key, environment="live")
                logger.info("oanda_live_mode_enabled", account_id=account_id)
            else:
                self.client = API(access_token=api_key)
                logger.info("oanda_practice_mode_enabled", account_id=account_id)
        else:
            self.client = None
            logger.warning("oanda_mock_mode_enabled", 
                         reason="invalid_or_missing_credentials",
                         note="Use valid OANDA credentials for live trading")
            
        logger.info("oanda_client_initialized", 
                   environment=self.environment, 
                   mock_mode=self.mock_mode)
    
    def _get_mock_price(self, instrument: str) -> float:
        """Generate realistic mock price for testing"""
        base_prices = {
            "EUR_USD": 1.1000,
            "GBP_USD": 1.2500,
            "USD_JPY": 150.00,
            "AUD_USD": 0.6500,
            "USD_CHF": 0.9000,
            "USD_CAD": 1.3500
        }
        base = base_prices.get(instrument, 1.0000)
        # Add small random variation (±0.1%)
        variation = random.uniform(-0.001, 0.001)
        return round(base * (1 + variation), self.oanda_price_precision(instrument))
    
    def _get_mock_spread(self, instrument: str) -> float:
        """Generate realistic mock spread for testing"""
        # Mock spreads in pips
        spreads = {"EUR_USD": 1.2, "GBP_USD": 1.5, "USD_JPY": 1.0}
        spread_pips = spreads.get(instrument, 1.2)
        return spread_pips * self.pip_size_for(instrument)
    
    def _get_mock_positions(self, instrument: Optional[str] = None) -> Dict[str, Any]:
        """Generate mock positions for testing"""
        if instrument:
            return {"has_position": False, "net_units": 0}
        else:
            return {}
    
    def oanda_price_precision(self, instrument: str) -> int:
        """Get price precision for instrument (delegated to canonical)"""
        return oanda_price_precision(instrument)
    
    def pip_size_for(self, instrument: str) -> float:
        """Get pip size for instrument (delegated to canonical)"""
        return pip_size_for(instrument)
    
    def oanda_min_trade_size(self, instrument: str) -> int:
        """Get minimum trade size for instrument (delegated to canonical)"""
        return oanda_min_trade_size(instrument)
    
    def _get_mock_candles(self, instrument: str, count: int) -> pd.DataFrame:
        """Generate mock candle data for testing"""
        import datetime
        base_price = self._get_mock_price(instrument)
        
        # Generate mock OHLC data
        data = []
        for i in range(count):
            # Random walk around base price
            open_price = base_price * (1 + random.uniform(-MOCK_PRICE_VARIANCE, MOCK_PRICE_VARIANCE))
            high_price = open_price * (1 + random.uniform(MOCK_HIGH_VARIANCE_MIN, MOCK_HIGH_VARIANCE_MAX))
            low_price = open_price * (1 - random.uniform(MOCK_LOW_VARIANCE_MIN, MOCK_LOW_VARIANCE_MAX))
            close_price = open_price * (1 + random.uniform(-MOCK_CLOSE_VARIANCE, MOCK_CLOSE_VARIANCE))
            volume = random.randint(MOCK_VOLUME_MIN, MOCK_VOLUME_MAX)
            
            timestamp = datetime.datetime.utcnow() - datetime.timedelta(minutes=5 * (count - i))
            
            data.append({
                'timestamp': timestamp.isoformat(),
                'open': round(open_price, self.oanda_price_precision(instrument)),
                'high': round(high_price, self.oanda_price_precision(instrument)),
                'low': round(low_price, self.oanda_price_precision(instrument)),
                'close': round(close_price, self.oanda_price_precision(instrument)),
                'volume': volume
            })
        
        return pd.DataFrame(data)
    
    async def get_current_price(self, instrument: str) -> Optional[float]:
        """Get current market price for an instrument"""
        if self.mock_mode:
            return self._get_mock_price(instrument)
            
        try:
            if not self.client:
                raise OandaClientNotInitialized()
                
            r = pricing.PricingInfo(
                accountID=self.account_id, 
                params={"instruments": instrument}
            )
            resp = self.client.request(r)
            
            if not isinstance(resp, dict):
                resp = next(iter(resp))
                
            price = float(resp["prices"][0]["closeoutBid"])
            logger.debug("price_fetched", instrument=instrument, price=price)
            return price
            
        except Exception as e:
            logger.error("price_fetch_failed", instrument=instrument, error=str(e))
            return None
    
    async def get_spread(self, instrument: str) -> Optional[float]:
        """Get current bid-ask spread for an instrument"""
        if self.mock_mode:
            return self._get_mock_spread(instrument)
            
        try:
            if not self.client:
                raise OandaClientNotInitialized()
                
            r = pricing.PricingInfo(
                accountID=self.account_id,
                params={"instruments": instrument}
            )
            resp = self.client.request(r)
            
            if not isinstance(resp, dict):
                resp = next(iter(resp))
                
            ask = float(resp["prices"][0]["closeoutAsk"])
            bid = float(resp["prices"][0]["closeoutBid"])
            spread = ask - bid
            
            logger.debug("spread_fetched", instrument=instrument, spread=spread)
            return spread
            
        except Exception as e:
            logger.error("spread_fetch_failed", instrument=instrument, error=str(e))
            return None
    
    async def get_candles(self, instrument: str, granularity: str = "M5", count: int = 100) -> Optional[pd.DataFrame]:
        """Get historical candle data for technical analysis"""
        if self.mock_mode:
            return self._get_mock_candles(instrument, count)
            
        try:
            if not self.client:
                raise OandaClientNotInitialized()
                
            candles_req = instruments.InstrumentsCandles(
                instrument=instrument,
                params={"granularity": granularity, "count": count}
            )
            candles_resp = self.client.request(candles_req)
            
            if not isinstance(candles_resp, dict):
                candles_resp = next(iter(candles_resp))
                
            candles = candles_resp.get("candles", [])
            
            # Convert to DataFrame for technical analysis
            data = []
            for candle in candles:
                if candle["complete"]:
                    data.append({
                        'timestamp': candle['time'],
                        'open': float(candle['mid']['o']),
                        'high': float(candle['mid']['h']),
                        'low': float(candle['mid']['l']),
                        'close': float(candle['mid']['c']),
                        'volume': int(candle['volume'])
                    })
            
            df = pd.DataFrame(data)
            logger.debug("candles_fetched", instrument=instrument, count=len(df))
            return df
            
        except Exception as e:
            logger.error("candles_fetch_failed", instrument=instrument, error=str(e))
            return None
    
    async def get_account_balance(self) -> Optional[float]:
        """Get account balance"""
        if self.mock_mode:
            return 10000.0  # Mock balance
            
        try:
            if not self.client:
                raise OandaClientNotInitialized()
                
            resp = self.client.request(accounts.AccountSummary(self.account_id))
            if not isinstance(resp, dict):
                resp = next(iter(resp))
                
            balance = float(resp['account']['balance'])
            logger.debug("balance_fetched", balance=balance)
            return balance
            
        except Exception as e:
            logger.error("balance_fetch_failed", error=str(e))
            return None
    
    async def get_open_positions(self, instrument: Optional[str] = None) -> Dict[str, Any]:
        """Get open positions, optionally filtered by instrument"""
        if self.mock_mode:
            return self._get_mock_positions(instrument)
            
        try:
            if not self.client:
                raise OandaClientNotInitialized()
                
            if instrument:
                resp = self.client.request(
                    positions.PositionDetails(self.account_id, instrument=instrument)
                )
                # Handle generator responses from OANDA API
                if not isinstance(resp, dict):
                    try:
                        resp = next(iter(resp), {})
                    except (TypeError, StopIteration):
                        resp = {}
                
                pos = resp.get("position", {}) if isinstance(resp, dict) else {}
                net_units = float(((pos.get("net") or {}).get("units")) or 0.0)
                
                return {
                    "instrument": instrument,
                    "net_units": net_units,
                    "has_position": abs(net_units) > 0
                }
            else:
                # Get all positions
                resp = self.client.request(positions.OpenPositions(self.account_id))
                if not isinstance(resp, dict):
                    resp = next(iter(resp))
                
                positions_data = {}
                for pos in resp.get("positions", []):
                    instrument = pos["instrument"]
                    net_units = float(pos["net"]["units"])
                    positions_data[instrument] = {
                        "net_units": net_units,
                        "has_position": abs(net_units) > 0
                    }
                
                return positions_data
                
        except Exception as e:
            logger.error("positions_fetch_failed", error=str(e))
            return {}
    

