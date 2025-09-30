"""
OANDA API integration for market data retrieval.
Handles real-time pricing, account information, and position data.
"""

import logging
from oandapyV20 import API
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.instruments as instruments
from typing import Dict, List, Optional, Any

class MarketDataProvider:
    def __init__(self, api_key: str, account_id: str, environment: str = "practice"):
        self.api_key = api_key
        self.account_id = account_id
        self.environment = environment
        
        if environment == "live":
            self.client = API(access_token=api_key, environment="live")
        else:
            self.client = API(access_token=api_key)
    
    def get_current_price(self, instrument: str) -> Optional[Dict[str, float]]:
        """Get current bid/ask prices for an instrument."""
        try:
            r = pricing.PricingInfo(accountID=self.account_id, params={"instruments": instrument})
            resp = self.client.request(r)
            
            if not isinstance(resp, dict):
                resp = next(iter(resp))
            
            price_data = resp["prices"][0]
            return {
                "bid": float(price_data["closeoutBid"]),
                "ask": float(price_data["closeoutAsk"]),
                "mid": (float(price_data["closeoutBid"]) + float(price_data["closeoutAsk"])) / 2,
                "spread": float(price_data["closeoutAsk"]) - float(price_data["closeoutBid"])
            }
        except Exception as e:
            logging.error(f"Failed to get current price for {instrument}: {e}")
            return None
    
    def get_account_summary(self) -> Optional[Dict[str, Any]]:
        """Get account balance and margin information."""
        try:
            r = accounts.AccountSummary(self.account_id)
            resp = self.client.request(r)
            
            if not isinstance(resp, dict):
                resp = next(iter(resp))
            
            account_data = resp['account']
            return {
                "balance": float(account_data['balance']),
                "equity": float(account_data.get('NAV', account_data['balance'])),
                "margin_available": float(account_data.get('marginAvailable', 0.0)),
                "margin_used": float(account_data.get('marginUsed', 0.0)),
                "unrealized_pl": float(account_data.get('unrealizedPL', 0.0))
            }
        except Exception as e:
            logging.error(f"Failed to get account summary: {e}")
            return None
    
    def get_position_details(self, instrument: str) -> Optional[Dict[str, Any]]:
        """Get position details for a specific instrument."""
        try:
            r = positions.PositionDetails(self.account_id, instrument=instrument)
            resp = self.client.request(r)
            
            if hasattr(resp, '__iter__') and not isinstance(resp, dict):
                resp = next(iter(resp), {})
            
            if not isinstance(resp, dict):
                resp = {}
            
            pos = resp.get("position", {})
            net_units = float(((pos.get("net") or {}).get("units")) or 0.0)
            
            return {
                "net_units": net_units,
                "long_units": float(((pos.get("long") or {}).get("units")) or 0.0),
                "short_units": float(((pos.get("short") or {}).get("units")) or 0.0),
                "unrealized_pl": float(((pos.get("net") or {}).get("unrealizedPL")) or 0.0)
            }
        except Exception as e:
            logging.error(f"Failed to get position details for {instrument}: {e}")
            return {"net_units": 0.0, "long_units": 0.0, "short_units": 0.0, "unrealized_pl": 0.0}
    
    def get_candle_data(self, instrument: str, granularity: str = "M5", count: int = 100) -> List[Dict[str, Any]]:
        """Get historical candle data for technical analysis."""
        try:
            r = instruments.InstrumentsCandles(
                instrument=instrument,
                params={"granularity": granularity, "count": count}
            )
            resp = self.client.request(r)
            
            if not isinstance(resp, dict):
                resp = next(iter(resp))
            
            candles = resp.get("candles", [])
            
            # Convert to list of dictionaries with OHLC data
            candle_data = []
            for candle in candles:
                if candle.get("complete", False):
                    candle_data.append({
                        "time": candle["time"],
                        "open": float(candle["mid"]["o"]),
                        "high": float(candle["mid"]["h"]),
                        "low": float(candle["mid"]["l"]),
                        "close": float(candle["mid"]["c"]),
                        "volume": int(candle.get("volume", 0))
                    })
            
            return candle_data
        except Exception as e:
            logging.error(f"Failed to get candle data for {instrument}: {e}")
            return []
    
    def get_pip_size(self, instrument: str) -> float:
        """Get pip size for an instrument."""
        if instrument.endswith('JPY'):
            return 0.01
        return 0.0001
    
    def calculate_spread_pips(self, instrument: str, spread: float) -> float:
        """Calculate spread in pips."""
        pip_size = self.get_pip_size(instrument)
        return spread / pip_size
