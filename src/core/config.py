from pydantic_settings import BaseSettings
from typing import List, Dict, Any
import os

class TradingConfig:
    def __init__(self):
        self.instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]
        self.poll_interval = 10  # seconds
        self.strategies = {
            "main_trend_following": {
                "sl_pips": 15,
                "tp_pips": 30,
                "risk_frac": 0.01,
                "adx_min": 20,
                "rsi_oversold": 30,
                "rsi_overbought": 70
            }
        }
        self.filters = {
            "max_spread_pips": 2.0,
            "weekend_block": True,
            "correlation_threshold": 0.5
        }

class Settings(BaseSettings):
    APP_NAME: str = "Trading Signal Alerts"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # OANDA Configuration
    OANDA_API_KEY: str = ""
    OANDA_ACCOUNT_ID: str = ""
    OANDA_ENV: str = "practice"  # practice or live
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_PRIVATE_KEY: str = ""
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Redis (optional for caching)
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def TRADING_CONFIG(self) -> TradingConfig:
        return TradingConfig()

settings = Settings()
