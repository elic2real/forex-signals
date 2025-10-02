"""
System 2.1: GSSI/CAR Engine & Market Regime Classification (MRC)
Implementation of F.1 (GSSI/CAR) and O (MRC) requirements
"""

from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime, timedelta
import json
import numpy as np
from enum import Enum
import pickle
import os

class MarketRegime(Enum):
    TRENDING_BULL = "trending_bull"
    TRENDING_BEAR = "trending_bear" 
    RANGING_HIGH_VOL = "ranging_high_vol"
    RANGING_LOW_VOL = "ranging_low_vol"
    CRISIS_MODE = "crisis_mode"
    RECOVERY_MODE = "recovery_mode"

class GSSICAREngine:
    """
    Global Systemic Stress Indicator (GSSI) & Concentrated Alpha Risk (CAR) Engine
    Implementation of F.1: GSSI/CAR calculation and dynamic sizing integration
    """
    
    def __init__(self):
        self.gssi_components = {
            "vix_component": 0.3,       # VIX stress weight
            "correlation_component": 0.25,  # Cross-asset correlation
            "liquidity_component": 0.25,    # Bid-ask spread stress
            "momentum_component": 0.2       # Momentum breakdown
        }
        self.car_alpha_threshold = Decimal('0.15')  # 15% alpha concentration limit
        
    def calculate_gssi_score(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Global Systemic Stress Indicator
        Range: 0.0 (no stress) to 1.0 (extreme stress)
        """
        from src.core.trace_logger import system_logger, TraceContext
        
        # VIX stress component (normalized)
        vix_level = market_data.get("vix", 20.0)
        vix_stress = min(1.0, max(0.0, (vix_level - 12.0) / 50.0))  # Normalize 12-62 range
        
        # Cross-asset correlation component
        correlations = market_data.get("correlations", {})
        avg_correlation = np.mean(list(correlations.values())) if correlations else 0.6
        correlation_stress = min(1.0, max(0.0, (avg_correlation - 0.3) / 0.6))  # High correlation = stress
        
        # Liquidity stress (spread widening)
        spreads = market_data.get("spreads", {})
        avg_spread = np.mean(list(spreads.values())) if spreads else 1.5
        normal_spread = 1.0
        liquidity_stress = min(1.0, max(0.0, (avg_spread - normal_spread) / (5.0 - normal_spread)))
        
        # Momentum breakdown (trend inconsistency)
        momentum_signals = market_data.get("momentum_breakdown", 0.3)
        
        # Weighted GSSI calculation
        gssi_score = (
            self.gssi_components["vix_component"] * vix_stress +
            self.gssi_components["correlation_component"] * correlation_stress +
            self.gssi_components["liquidity_component"] * liquidity_stress +
            self.gssi_components["momentum_component"] * momentum_signals
        )
        
        gssi_result = {
            "gssi_score": round(gssi_score, 4),
            "components": {
                "vix_stress": round(vix_stress, 4),
                "correlation_stress": round(correlation_stress, 4), 
                "liquidity_stress": round(liquidity_stress, 4),
                "momentum_breakdown": round(momentum_signals, 4)
            },
            "raw_inputs": {
                "vix_level": vix_level,
                "avg_correlation": round(avg_correlation, 4),
                "avg_spread": round(avg_spread, 4)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        system_logger.logger.info("GSSI_CALCULATED", **gssi_result)
        return gssi_result
    
    def calculate_car_score(self, portfolio_data: Dict[str, Any], gssi_score: float) -> Dict[str, Any]:
        """
        Calculate Concentrated Alpha Risk (CAR) score
        Combines position concentration with GSSI stress
        """
        from src.core.trace_logger import system_logger
        
        # Position concentration analysis
        positions = portfolio_data.get("positions", [])
        total_exposure = sum([abs(pos.get("notional", 0)) for pos in positions])
        
        if total_exposure == 0:
            concentration_risk = 0.0
        else:
            # Calculate Herfindahl index for concentration
            exposures = [abs(pos.get("notional", 0)) / total_exposure for pos in positions]
            herfindahl_index = sum([exp**2 for exp in exposures])
            concentration_risk = min(1.0, herfindahl_index * 2.0)  # Scale to 0-1
        
        # Alpha concentration (strategy-specific)
        strategy_exposures = portfolio_data.get("strategy_exposures", {})
        max_strategy_pct = max(strategy_exposures.values()) if strategy_exposures else 0.0
        alpha_concentration = min(1.0, max_strategy_pct / float(self.car_alpha_threshold))
        
        # CAR combines concentration with GSSI stress
        car_score = (concentration_risk * 0.4 + alpha_concentration * 0.3 + gssi_score * 0.3)
        
        car_result = {
            "car_score": round(car_score, 4),
            "concentration_risk": round(concentration_risk, 4),
            "alpha_concentration": round(alpha_concentration, 4),
            "gssi_influence": round(gssi_score * 0.3, 4),
            "position_count": len(positions),
            "total_exposure": total_exposure,
            "max_strategy_pct": round(max_strategy_pct, 4),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        system_logger.logger.info("CAR_CALCULATED", **car_result)
        return car_result
    
    def apply_dynamic_leverage_adjustment(self, base_leverage: Decimal, 
                                        gssi_score: float, car_score: float) -> Dict[str, Any]:
        """
        F.1: Apply dynamic leverage based on GSSI/CAR cascade
        Higher stress = Lower leverage
        """
        from src.core.trace_logger import system_logger
        
        # GSSI adjustment factor
        if gssi_score >= 0.8:
            gssi_multiplier = Decimal('0.4')  # 60% reduction
        elif gssi_score >= 0.6:
            gssi_multiplier = Decimal('0.6')  # 40% reduction
        elif gssi_score >= 0.4:
            gssi_multiplier = Decimal('0.8')  # 20% reduction
        else:
            gssi_multiplier = Decimal('1.0')  # No reduction
        
        # CAR adjustment factor
        if car_score >= 0.7:
            car_multiplier = Decimal('0.5')   # 50% reduction
        elif car_score >= 0.5:
            car_multiplier = Decimal('0.75')  # 25% reduction
        else:
            car_multiplier = Decimal('1.0')   # No reduction
        
        # Combined adjustment (multiplicative)
        combined_multiplier = gssi_multiplier * car_multiplier
        adjusted_leverage = base_leverage * combined_multiplier
        
        # Ensure we don't exceed max leverage
        final_leverage = min(adjusted_leverage, Decimal('50.0'))
        
        adjustment_result = {
            "base_leverage": float(base_leverage),
            "gssi_score": gssi_score,
            "car_score": car_score,
            "gssi_multiplier": float(gssi_multiplier),
            "car_multiplier": float(car_multiplier),
            "combined_multiplier": float(combined_multiplier),
            "adjusted_leverage": float(adjusted_leverage),
            "final_leverage": float(final_leverage),
            "reduction_pct": float((1 - combined_multiplier) * 100)
        }
        
        system_logger.logger.info("DYNAMIC_LEVERAGE_APPLIED", **adjustment_result)
        return adjustment_result

class MarketRegimeClassifier:
    """
    Market Regime Classification (MRC) Engine
    Implementation of O: MRC with 6 regime-specific weight profiles and smooth transitions
    """
    
    def __init__(self, profile_storage_path: str = "config/regime_profiles.pkl"):
        self.profile_storage_path = profile_storage_path
        self.confidence_threshold = 0.8  # 80% confidence for regime change
        self.current_regime = MarketRegime.RANGING_LOW_VOL
        self.regime_confidence = 0.5
        self.transition_smoothing_factor = 0.1  # For smooth weight transitions
        
        # Load or initialize regime-specific weight profiles
        self.regime_profiles = self._load_regime_profiles()
    
    def classify_market_regime(self, market_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify current market regime with confidence scoring
        Returns regime classification and confidence level
        """
        from src.core.trace_logger import system_logger
        
        # Extract key features
        volatility = market_features.get("volatility", 0.2)
        trend_strength = market_features.get("trend_strength", 0.0)
        volume_trend = market_features.get("volume_trend", 0.0)
        crisis_indicators = market_features.get("crisis_score", 0.0)
        
        # Regime classification logic
        regime_scores = {}
        
        # Trending Bull: High trend strength + Low volatility + Positive volume
        regime_scores[MarketRegime.TRENDING_BULL] = (
            max(0, trend_strength) * 0.4 +
            (1 - volatility) * 0.3 +
            max(0, volume_trend) * 0.3
        )
        
        # Trending Bear: High negative trend + Moderate volatility
        regime_scores[MarketRegime.TRENDING_BEAR] = (
            max(0, -trend_strength) * 0.4 +
            volatility * 0.3 +
            max(0, -volume_trend) * 0.3
        )
        
        # Ranging High Vol: Low trend + High volatility
        regime_scores[MarketRegime.RANGING_HIGH_VOL] = (
            (1 - abs(trend_strength)) * 0.5 +
            volatility * 0.5
        )
        
        # Ranging Low Vol: Low trend + Low volatility
        regime_scores[MarketRegime.RANGING_LOW_VOL] = (
            (1 - abs(trend_strength)) * 0.6 +
            (1 - volatility) * 0.4
        )
        
        # Crisis Mode: High crisis indicators
        regime_scores[MarketRegime.CRISIS_MODE] = crisis_indicators
        
        # Recovery Mode: Declining crisis + Positive momentum
        recovery_score = max(0, 1 - crisis_indicators) * max(0, trend_strength + volume_trend)
        regime_scores[MarketRegime.RECOVERY_MODE] = recovery_score
        
        # Determine best regime and confidence
        best_regime = max(regime_scores.keys(), key=lambda k: regime_scores[k])
        best_score = regime_scores[best_regime]
        
        # Calculate confidence as margin over second best
        sorted_scores = sorted(regime_scores.values(), reverse=True)
        confidence = best_score - (sorted_scores[1] if len(sorted_scores) > 1 else 0)
        confidence = min(1.0, confidence * 2)  # Scale to 0-1
        
        # Update current regime if confidence is high enough
        previous_regime = self.current_regime
        if confidence >= self.confidence_threshold:
            self.current_regime = best_regime
            self.regime_confidence = confidence
        
        classification_result = {
            "previous_regime": previous_regime.value,
            "current_regime": self.current_regime.value,
            "regime_changed": previous_regime != self.current_regime,
            "confidence": round(confidence, 4),
            "regime_scores": {regime.value: round(score, 4) for regime, score in regime_scores.items()},
            "market_features": market_features,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if previous_regime != self.current_regime:
            system_logger.logger.critical("REGIME_CHANGE_DETECTED", **classification_result)
        else:
            system_logger.logger.info("REGIME_CLASSIFICATION", **classification_result)
        
        return classification_result
    
    def get_current_weight_profile(self) -> Dict[str, float]:
        """Get current regime-specific weight profile for supervisor engine"""
        return self.regime_profiles.get(self.current_regime, self._get_default_profile())
    
    def apply_smooth_transition(self, old_profile: Dict[str, float], 
                              new_profile: Dict[str, float], 
                              transition_progress: float) -> Dict[str, float]:
        """
        O: Smooth transition function between regime weight profiles
        Prevents abrupt strategy weight changes
        """
        from src.core.trace_logger import system_logger
        
        # Linear interpolation between profiles
        smooth_profile = {}
        
        all_engines = set(old_profile.keys()) | set(new_profile.keys())
        
        for engine in all_engines:
            old_weight = old_profile.get(engine, 0.0)
            new_weight = new_profile.get(engine, 0.0)
            
            # Linear interpolation
            smooth_weight = old_weight + (new_weight - old_weight) * transition_progress
            smooth_profile[engine] = round(smooth_weight, 4)
        
        transition_result = {
            "old_profile": old_profile,
            "new_profile": new_profile,
            "transition_progress": transition_progress,
            "smooth_profile": smooth_profile,
            "regime": self.current_regime.value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        system_logger.logger.info("SMOOTH_TRANSITION_APPLIED", **transition_result)
        return smooth_profile
    
    def _load_regime_profiles(self) -> Dict[MarketRegime, Dict[str, float]]:
        """Load regime-specific weight profiles from storage"""
        if os.path.exists(self.profile_storage_path):
            try:
                with open(self.profile_storage_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading regime profiles: {e}")
        
        # Return default profiles if loading fails
        return self._create_default_profiles()
    
    def _create_default_profiles(self) -> Dict[MarketRegime, Dict[str, float]]:
        """Create default regime-specific weight profiles"""
        return {
            MarketRegime.TRENDING_BULL: {
                "technical_engine": 0.35,
                "fundamental_engine": 0.25,
                "sentiment_engine": 0.20,
                "correlation_engine": 0.10,
                "volatility_engine": 0.05,
                "news_engine": 0.05
            },
            MarketRegime.TRENDING_BEAR: {
                "technical_engine": 0.30,
                "fundamental_engine": 0.20,
                "sentiment_engine": 0.15,
                "correlation_engine": 0.15,
                "volatility_engine": 0.15,
                "news_engine": 0.05
            },
            MarketRegime.RANGING_HIGH_VOL: {
                "technical_engine": 0.25,
                "volatility_engine": 0.30,
                "correlation_engine": 0.20,
                "sentiment_engine": 0.15,
                "fundamental_engine": 0.05,
                "news_engine": 0.05
            },
            MarketRegime.RANGING_LOW_VOL: {
                "technical_engine": 0.40,
                "volatility_engine": 0.10,
                "correlation_engine": 0.25,
                "sentiment_engine": 0.15,
                "fundamental_engine": 0.10,
                "news_engine": 0.0
            },
            MarketRegime.CRISIS_MODE: {
                "sentiment_engine": 0.35,
                "news_engine": 0.25,
                "volatility_engine": 0.20,
                "correlation_engine": 0.15,
                "technical_engine": 0.05,
                "fundamental_engine": 0.0
            },
            MarketRegime.RECOVERY_MODE: {
                "fundamental_engine": 0.35,
                "technical_engine": 0.25,
                "sentiment_engine": 0.20,
                "volatility_engine": 0.10,
                "correlation_engine": 0.10,
                "news_engine": 0.0
            }
        }
    
    def _get_default_profile(self) -> Dict[str, float]:
        """Get default balanced profile"""
        return {
            "technical_engine": 0.25,
            "fundamental_engine": 0.20,
            "sentiment_engine": 0.20,
            "correlation_engine": 0.15,
            "volatility_engine": 0.15,
            "news_engine": 0.05
        }
    
    def save_regime_profiles(self):
        """Save current regime profiles to storage"""
        try:
            os.makedirs(os.path.dirname(self.profile_storage_path), exist_ok=True)
            with open(self.profile_storage_path, 'wb') as f:
                pickle.dump(self.regime_profiles, f)
        except Exception as e:
            print(f"Error saving regime profiles: {e}")

# Global instances
gssi_car_engine = GSSICAREngine()
market_regime_classifier = MarketRegimeClassifier()