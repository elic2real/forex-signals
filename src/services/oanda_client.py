"""OANDA API client for market data and account information"""

import structlog
from oandapyV20 import API
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.positions as positions
from typing import Dict, List, Optional, Any
import pandas as pd

logger = structlog.get_logger()

class OandaClient:
    def __init__(self, api_key: str, account_id: str, environment: str = "practice"):
        self.api_key = api_key
        self.account_id = account_id
        self.environment = environment
        
        if environment == "live":
            self.client = API(access_token=api_key, environment="live")
        else:
            self.client = API(access_token=api_key)
            
        logger.info("oanda_client_initialized", environment=environment)
    
    async def get_current_price(self, instrument: str) -> Optional[float]:
        """Get current market price for an instrument"""
        try:
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
        try:
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
        try:
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
        try:
            resp = self.client.request(accounts.AccountSummary(self.account_id))
            if not isinstance(resp, dict):
                resp = next(iter(resp))
                
            balance = float(resp['account']['balance'])
            logger.debug("balance_fetched", balance=balance)
            return balance
            
        except Exception as e:
            logger.error("balance_fetch_failed", error=str(e))
            return None
    
    async def get_open_positions(self, instrument: str = None) -> Dict[str, Any]:
        """Get open positions, optionally filtered by instrument"""
        try:
            if instrument:
                resp = self.client.request(
                    positions.PositionDetails(self.account_id, instrument=instrument)
                )
                if hasattr(resp, '__iter__') and not isinstance(resp, dict):
                    resp = next(iter(resp), {})
                
                pos = resp.get("position", {})
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
    
    def pip_size_for(self, instrument: str) -> float:
        """Get pip size for an instrument"""
        if instrument.endswith('JPY'):
            return 0.01
        return 0.0001
