"""Signal generation engine - extracts trading logic for alerting"""

import structlog
import asyncio
import pandas as pd
import pandas_ta as ta
import yfinance as yf
from datetime import datetime
from typing import Dict, Any, Optional, List
import numpy as np

from .oanda_client import OandaClient
from .fcm_service import FCMService

logger = structlog.get_logger()

class SignalEngine:
    def __init__(self, oanda_client: OandaClient, fcm_service: FCMService, config: Any):
        self.oanda_client = oanda_client
        self.fcm_service = fcm_service
        self.config = config
        self.monitoring = False
        self.device_tokens: List[str] = []  # Will be populated by mobile app registrations
        
    async def start_monitoring(self):
        """Start the signal monitoring loop"""
        self.monitoring = True
        logger.info("signal_monitoring_started")
        
        # Start background task
        asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Stop the signal monitoring loop"""
        self.monitoring = False
        logger.info("signal_monitoring_stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop - checks for signals periodically"""
        while self.monitoring:
            try:
                for instrument in self.config.instruments:
                    await self._check_instrument_signals(instrument)
                
                # Wait before next check
                await asyncio.sleep(self.config.poll_interval)
                
            except Exception as e:
                logger.error("monitoring_loop_error", error=str(e))
                await asyncio.sleep(5)  # Short delay on error
    
    async def _check_instrument_signals(self, instrument: str):
        """Check for trading signals on a specific instrument"""
        try:
            logger.debug("checking_signals", instrument=instrument)
            
            # Skip if already have position (exposure check)
            positions = await self.oanda_client.get_open_positions(instrument)
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
                
                max_spread = self.config.filters.get("max_spread_pips", 2.0)
                if spread_pips > max_spread:
                    logger.debug("spread_too_wide", instrument=instrument, spread_pips=spread_pips)
                    return
            
            # Weekend block
            if self.config.filters.get("weekend_block", True):
                now = datetime.utcnow()
                if now.weekday() == 5 or (now.weekday() == 6 and now.hour < 22):
                    logger.debug("weekend_block_active", instrument=instrument)
                    return
            
            # Get candle data for technical analysis
            df = await self.oanda_client.get_candles(instrument, granularity="M5", count=100)
            if df is None or len(df) < 60:
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
            # Calculate indicators
            df["ema20"] = ta.ema(df["close"], length=20)
            df["ema50"] = ta.ema(df["close"], length=50)
            df["rsi"] = ta.rsi(df["close"], length=14)
            df["adx"] = ta.adx(df["high"], df["low"], df["close"], length=14)["ADX_14"]
            
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
