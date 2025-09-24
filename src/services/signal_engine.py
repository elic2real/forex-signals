"""Signal generation engine - extracts trading logic for alerting"""

import structlog
import asyncio
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import numpy as np
import math

from .oanda_client import OandaClient
from .fcm_service import FCMService

logger = structlog.get_logger()

# Performance constants
ERROR_RETRY_DELAY_SECONDS = 5
WEEKEND_SATURDAY = 5  # Saturday weekday number
WEEKEND_SUNDAY = 6    # Sunday weekday number  
SUNDAY_MARKET_OPEN_HOUR = 22  # Markets open Sunday 22:00 UTC
MIN_CANDLES_FOR_ANALYSIS = 60
DEFAULT_MAX_SPREAD_PIPS = 2.0
CANDLE_GRANULARITY = "M5"
CANDLE_COUNT = 100

# Caching for performance
_position_cache = {}
_position_cache_expiry = {}
POSITION_CACHE_DURATION_SECONDS = 30

def calculate_ema(prices: pd.Series, length: int) -> pd.Series:
    """Calculate Exponential Moving Average"""
    # Ensure numeric data
    prices = pd.to_numeric(prices, errors='coerce')
    return prices.ewm(span=length, adjust=False).mean()

def calculate_rsi(prices: pd.Series, length: int = 14) -> pd.Series:
    """Calculate Relative Strength Index"""
    try:
        # Ensure numeric data
        prices = pd.to_numeric(prices, errors='coerce').dropna()
        if len(prices) < length:
            return pd.Series([np.nan] * len(prices), index=prices.index)
            
        delta = prices.diff()
        gain = delta.clip(lower=0).rolling(window=length).mean()
        loss = (-delta.clip(upper=0)).rolling(window=length).mean()
        
        # Avoid division by zero
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi
    except Exception as e:
        logger.warning("rsi_calculation_failed", error=str(e))
        return pd.Series([50.0] * len(prices), index=prices.index)  # Neutral RSI

def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
    """Calculate Average Directional Index (simplified version)"""
    try:
        # Ensure numeric data
        high = pd.to_numeric(high, errors='coerce').dropna()
        low = pd.to_numeric(low, errors='coerce').dropna()
        close = pd.to_numeric(close, errors='coerce').dropna()
        
        if len(high) < length or len(low) < length or len(close) < length:
            return pd.Series([20.0] * len(close), index=close.index)  # Default ADX
            
        # Simplified ADX - just return a basic trend strength measure
        # Based on price volatility and direction
        high_low_range = (high - low).rolling(window=length).mean()
        close_change = close.diff().abs().rolling(window=length).mean()
        
        # Simple trend strength proxy
        trend_strength = (close_change / high_low_range * 50).fillna(20.0)
        return trend_strength.clip(0, 100)
        
    except Exception as e:
        logger.warning("adx_calculation_failed", error=str(e))
        return pd.Series([20.0] * len(close), index=close.index)  # Default ADX

class SignalEngine:
    def __init__(self, oanda_client: OandaClient, fcm_service: FCMService, config: Any):
        self.oanda_client = oanda_client
        self.fcm_service = fcm_service
        self.config = config
        self.monitoring = False
        self.device_tokens: List[str] = []  # Will be populated by mobile app registrations
        self._monitoring_task: Optional[asyncio.Task] = None
        
    async def start_monitoring(self):
        """Start the signal monitoring loop"""
        if self.monitoring:
            logger.warning("signal_monitoring_already_active")
            return
            
        self.monitoring = True
        logger.info("signal_monitoring_started")
        
        # Start background task and store reference
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Stop the signal monitoring loop"""
        self.monitoring = False
        logger.info("signal_monitoring_stopped")
        
        # Cancel the monitoring task if it exists
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
    
    async def _monitoring_loop(self):
        """Main monitoring loop - checks for signals periodically"""
        try:
            logger.info("monitoring_loop_started", instruments=self.config.instruments)
            while self.monitoring:
                try:
                    for instrument in self.config.instruments:
                        try:
                            await self._check_instrument_signals(instrument)
                        except Exception as e:
                            logger.error("instrument_signal_check_failed", 
                                       instrument=instrument, error=str(e))
                    
                    # Wait before next check
                    await asyncio.sleep(self.config.poll_interval)
                    
                except Exception as e:
                    logger.error("monitoring_loop_iteration_error", error=str(e))
                    await asyncio.sleep(ERROR_RETRY_DELAY_SECONDS)  # Short delay on error
        except asyncio.CancelledError:
            logger.info("monitoring_loop_cancelled")
            raise
        except Exception as e:
            logger.error("monitoring_loop_fatal_error", error=str(e))
        finally:
            logger.info("monitoring_loop_ended")
    
    async def _check_instrument_signals(self, instrument: str):
        """Check for trading signals on a specific instrument"""
        try:
            logger.debug("checking_signals", instrument=instrument)
            
            # Skip if already have position (exposure check) with caching
            positions = await self._get_positions_cached(instrument)
            if positions.get("has_position", False):
                logger.debug("position_exists_skipping", instrument=instrument)
                return
            
            # Get market data
            price = await self.oanda_client.get_current_price(instrument)
            if not price:
                return
            
            # Spread filter
            spread = await self.oanda_client.get_spread(instrument)
            if spread:
                pip_size = self.oanda_client.pip_size_for(instrument)
                spread_pips = spread / pip_size
                
                max_spread = self.config.filters.get("max_spread_pips", DEFAULT_MAX_SPREAD_PIPS)
                if spread_pips > max_spread:
                    logger.debug("spread_too_wide", instrument=instrument, spread_pips=spread_pips)
                    return
            
            # Weekend block with constants
            if self.config.filters.get("weekend_block", True):
                now = datetime.utcnow()
                if (now.weekday() == WEEKEND_SATURDAY or 
                    (now.weekday() == WEEKEND_SUNDAY and now.hour < SUNDAY_MARKET_OPEN_HOUR)):
                    logger.debug("weekend_block_active", instrument=instrument)
                    return
            
            # Get candle data for technical analysis
            df = await self.oanda_client.get_candles(instrument, 
                                                   granularity=CANDLE_GRANULARITY, 
                                                   count=CANDLE_COUNT)
            if df is None or len(df) < MIN_CANDLES_FOR_ANALYSIS:
                logger.debug("insufficient_candle_data", instrument=instrument)
                return
            
            # Apply correlation filter (SPY/EURUSD example)
            if instrument == "EUR_USD":
                correlation_ok = await self._check_correlation_filter()
                if not correlation_ok:
                    return
            
            # Technical analysis
            signal_strength = await self._analyze_technical_signals(df, instrument)
            
            if signal_strength != 0:
                # Generate alert
                await self._generate_signal_alert(instrument, price, signal_strength)
                
        except Exception as e:
            logger.error("signal_check_failed", instrument=instrument, error=str(e))
    
    async def _check_correlation_filter(self) -> bool:
        """Check SPY/EURUSD correlation filter"""
        # Use mock mode for development/testing
        if hasattr(self.oanda_client, 'mock_mode') and self.oanda_client.mock_mode:
            logger.debug("correlation_filter_mock_passed")
            return True
            
        try:
            spy = yf.download('SPY', period='30d', interval='1d', progress=False)
            eurusd = yf.download('EURUSD=X', period='30d', interval='1d', progress=False)
            
            if isinstance(spy, pd.DataFrame) and isinstance(eurusd, pd.DataFrame) and not spy.empty and not eurusd.empty:
                df_corr = pd.DataFrame({
                    'SPY': spy['Close'],
                    'EURUSD': eurusd['Close']
                }).dropna()
                
                corr = df_corr['SPY'].pct_change().corr(df_corr['EURUSD'].pct_change())
                
                threshold = self.config.filters.get("correlation_threshold", 0.5)
                if abs(corr) >= threshold:
                    logger.debug("correlation_too_strong", correlation=corr)
                    return False
                    
                logger.debug("correlation_check_passed", correlation=corr)
                return True
                
        except Exception as e:
            logger.warning("correlation_check_failed", error=str(e))
            
        return True  # Default to allowing trades if correlation check fails
    
    async def _analyze_technical_signals(self, df: pd.DataFrame, instrument: str) -> float:
        """Apply technical analysis to generate signals"""
        try:
            # Calculate indicators using our custom functions
            df["ema20"] = calculate_ema(df["close"], length=20)
            df["ema50"] = calculate_ema(df["close"], length=50)
            df["rsi"] = calculate_rsi(df["close"], length=14)
            df["adx"] = calculate_adx(df["high"], df["low"], df["close"], length=14)
            
            # Get strategy config
            strategy_config = self.config.strategies.get("main_trend_following", {})
            adx_min = strategy_config.get("adx_min", 20)
            rsi_oversold = strategy_config.get("rsi_oversold", 30)
            rsi_overbought = strategy_config.get("rsi_overbought", 70)
            
            # Current values
            current_adx = df["adx"].iloc[-1]
            current_rsi = df["rsi"].iloc[-1]
            current_ema20 = df["ema20"].iloc[-1]
            current_ema50 = df["ema50"].iloc[-1]
            
            # ADX filter (trend strength)
            if current_adx < adx_min:
                logger.debug("adx_too_low", instrument=instrument, adx=current_adx)
                return 0.0
            
            # Signal generation logic (from your main.py)
            # Strong uptrend: ADX>25, RSI>55, EMA20>EMA50
            if (current_adx > 25 and 
                current_rsi > 55 and 
                current_ema20 > current_ema50):
                logger.info("bullish_signal_detected", 
                           instrument=instrument, 
                           adx=current_adx, 
                           rsi=current_rsi)
                return 1.0
            
            # Strong downtrend: ADX>25, RSI<45, EMA20<EMA50
            elif (current_adx > 25 and 
                  current_rsi < 45 and 
                  current_ema20 < current_ema50):
                logger.info("bearish_signal_detected", 
                           instrument=instrument, 
                           adx=current_adx, 
                           rsi=current_rsi)
                return -1.0
            
            return 0.0
            
        except Exception as e:
            logger.error("technical_analysis_failed", instrument=instrument, error=str(e))
            return 0.0
    
    async def _generate_signal_alert(self, instrument: str, price: float, signal_strength: float):
        """Generate and send trading signal alert"""
        try:
            direction = "BUY" if signal_strength > 0 else "SELL"
            
            # Get strategy config for SL/TP levels
            strategy_config = self.config.strategies.get("main_trend_following", {})
            sl_pips = strategy_config.get("sl_pips", 15)
            tp_pips = strategy_config.get("tp_pips", 30)
            
            signal_data = {
                "signal_type": "ENTRY",
                "instrument": instrument,
                "direction": direction,
                "price": price,
                "sl_pips": sl_pips,
                "tp_pips": tp_pips,
                "confidence": abs(signal_strength),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send FCM notification if devices are registered
            if self.device_tokens:
                result = await self.fcm_service.send_signal_notification(
                    self.device_tokens, 
                    signal_data
                )
                
                logger.info("signal_alert_sent", 
                           signal_data=signal_data,
                           fcm_result=result)
            else:
                logger.info("signal_generated_no_devices", signal_data=signal_data)
                
        except Exception as e:
            logger.error("signal_alert_failed", error=str(e))
    
    async def _get_positions_cached(self, instrument: str) -> Dict[str, Any]:
        """Get position data with caching for performance"""
        global _position_cache, _position_cache_expiry
        
        now = datetime.utcnow()
        cache_key = instrument
        
        # Check if we have valid cached data
        if (cache_key in _position_cache and 
            cache_key in _position_cache_expiry and
            now < _position_cache_expiry[cache_key]):
            return _position_cache[cache_key]
        
        # Fetch fresh data
        positions = await self.oanda_client.get_open_positions(instrument)
        
        # Cache the result
        _position_cache[cache_key] = positions
        _position_cache_expiry[cache_key] = now + timedelta(seconds=POSITION_CACHE_DURATION_SECONDS)
        
        return positions
    
    def register_device(self, device_token: str):
        """Register a mobile device for notifications"""
        if device_token not in self.device_tokens:
            self.device_tokens.append(device_token)
            logger.info("device_registered", token_preview=device_token[:20] + "...")
    
    def unregister_device(self, device_token: str):
        """Unregister a mobile device"""
        if device_token in self.device_tokens:
            self.device_tokens.remove(device_token)
            logger.info("device_unregistered", token_preview=device_token[:20] + "...")
