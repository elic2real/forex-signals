"""
System 2.1: Ollama LLM Integration Engine
Implementation of K.1, K.2 requirements for AI-driven market analysis
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from decimal import Decimal
import ollama
from enum import Enum

class LLMTier(Enum):
    TIER_1 = "tier_1"  # Core market structure analysis
    TIER_2 = "tier_2"  # Sentiment and news processing
    TIER_3 = "tier_3"  # A/B tested experimental features

class OllamaLLMEngine:
    """
    Production-grade Ollama integration for System 2.1
    Handles market analysis, sentiment processing, and feature extraction
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.client = ollama.Client(host=base_url)
        self.models = {
            "market_analysis": "llama3.1:8b",  # Primary market analysis
            "sentiment": "llama3.1:8b",        # News sentiment
            "risk_assessment": "llama3.1:8b",  # Risk evaluation
            "pattern_recognition": "llama3.1:8b"  # Chart patterns
        }
        self.ab_test_enabled = True
        self.tier_3_sample_rate = 0.1  # 10% of trades use experimental features
    
    async def analyze_market_structure(self, 
                                     instrument: str, 
                                     price_data: Dict[str, Any],
                                     tier: LLMTier = LLMTier.TIER_1) -> Dict[str, Any]:
        """
        Tier 1: Core market structure analysis using Ollama
        """
        from src.core.trace_logger import system_logger, TraceContext
        
        prompt = self._build_market_analysis_prompt(instrument, price_data)
        
        try:
            response = await asyncio.to_thread(
                self.client.chat,
                model=self.models["market_analysis"],
                messages=[{
                    "role": "system",
                    "content": "You are an expert forex market structure analyst. Analyze the provided data and return structured JSON with support/resistance levels, trend direction, and confidence scores."
                }, {
                    "role": "user", 
                    "content": prompt
                }],
                options={
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 500
                }
            )
            
            analysis = self._parse_llm_response(response['message']['content'])
            
            result = {
                "tier": tier.value,
                "instrument": instrument,
                "analysis": analysis,
                "confidence": analysis.get("confidence", 0.5),
                "timestamp": datetime.utcnow().isoformat(),
                "trace_id": TraceContext.get_trace_id()
            }
            
            system_logger.logger.info("LLM_MARKET_ANALYSIS", **result)
            return result
            
        except Exception as e:
            system_logger.logger.error("LLM_ANALYSIS_ERROR", 
                                     instrument=instrument,
                                     tier=tier.value,
                                     error=str(e))
            return self._fallback_analysis(instrument)
    
    async def process_news_sentiment(self, 
                                   news_items: List[Dict[str, Any]], 
                                   instrument: str) -> Dict[str, Any]:
        """
        Tier 2: News sentiment analysis with impact scoring
        """
        from src.core.trace_logger import system_logger
        
        if not news_items:
            return {"sentiment_score": 0.0, "impact_level": "none"}
        
        news_text = "\n".join([item.get("headline", "") + " " + item.get("summary", "") 
                              for item in news_items[:5]])  # Process top 5 items
        
        prompt = f"""
        Analyze the following forex news for instrument {instrument}:
        
        {news_text}
        
        Return JSON with:
        - sentiment_score: float between -1.0 (very bearish) and 1.0 (very bullish)
        - impact_level: "low", "medium", "high"
        - key_themes: list of main themes
        - time_horizon: "immediate", "short_term", "medium_term"
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat,
                model=self.models["sentiment"],
                messages=[{
                    "role": "system",
                    "content": "You are an expert forex news analyst. Analyze sentiment and market impact of news events."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                options={"temperature": 0.2}
            )
            
            sentiment_analysis = self._parse_llm_response(response['message']['content'])
            
            result = {
                "instrument": instrument,
                "sentiment_score": sentiment_analysis.get("sentiment_score", 0.0),
                "impact_level": sentiment_analysis.get("impact_level", "low"),
                "key_themes": sentiment_analysis.get("key_themes", []),
                "time_horizon": sentiment_analysis.get("time_horizon", "short_term"),
                "news_count": len(news_items)
            }
            
            system_logger.logger.info("LLM_NEWS_SENTIMENT", **result)
            return result
            
        except Exception as e:
            system_logger.logger.error("LLM_SENTIMENT_ERROR", 
                                     instrument=instrument,
                                     error=str(e))
            return {"sentiment_score": 0.0, "impact_level": "none"}
    
    async def extract_tier3_features(self, 
                                   market_data: Dict[str, Any], 
                                   instrument: str) -> Optional[Dict[str, Any]]:
        """
        Tier 3: A/B tested experimental feature extraction
        K.2: LLM Feature Hunt A/B Test implementation
        """
        from src.core.trace_logger import system_logger
        import random
        
        # A/B test sampling
        if not self.ab_test_enabled or random.random() > self.tier_3_sample_rate:
            return None
        
        prompt = f"""
        Extract experimental trading features from this market data for {instrument}:
        
        {json.dumps(market_data, indent=2)}
        
        Look for:
        - Volume-price divergences
        - Hidden momentum patterns 
        - Cross-timeframe alignments
        - Unusual correlation patterns
        
        Return JSON with feature scores 0.0-1.0 for each pattern found.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat,
                model=self.models["pattern_recognition"],
                messages=[{
                    "role": "system",
                    "content": "You are an experimental trading feature researcher. Find novel patterns that traditional indicators miss."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                options={"temperature": 0.4}
            )
            
            features = self._parse_llm_response(response['message']['content'])
            
            result = {
                "instrument": instrument,
                "tier": "tier_3_experimental",
                "features": features,
                "ab_test_group": "treatment",
                "sample_rate": self.tier_3_sample_rate,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            system_logger.logger.info("LLM_TIER3_FEATURES", **result)
            return result
            
        except Exception as e:
            system_logger.logger.error("LLM_TIER3_ERROR", 
                                     instrument=instrument,
                                     error=str(e))
            return None
    
    async def assess_black_swan_risk(self, 
                                   market_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Black Swan risk assessment for Sentinel Engine integration
        """
        from src.core.trace_logger import system_logger
        
        prompt = f"""
        Assess black swan/tail risk in current market conditions:
        
        {json.dumps(market_context, indent=2)}
        
        Return JSON with:
        - swan_score: float 0.0-1.0 (1.0 = extreme tail risk)
        - risk_factors: list of specific risk factors identified
        - recommended_mode: "protect", "pounce", or "stand_down"
        - confidence: float 0.0-1.0
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat,
                model=self.models["risk_assessment"],
                messages=[{
                    "role": "system",
                    "content": "You are a black swan risk specialist. Identify tail risks and regime changes."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                options={"temperature": 0.1}  # Low temperature for risk assessment
            )
            
            risk_assessment = self._parse_llm_response(response['message']['content'])
            
            result = {
                "swan_score": risk_assessment.get("swan_score", 0.0),
                "risk_factors": risk_assessment.get("risk_factors", []),
                "recommended_mode": risk_assessment.get("recommended_mode", "stand_down"),
                "confidence": risk_assessment.get("confidence", 0.5),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            system_logger.logger.info("LLM_SWAN_ASSESSMENT", **result)
            return result
            
        except Exception as e:
            system_logger.logger.error("LLM_SWAN_ERROR", error=str(e))
            return {
                "swan_score": 0.5,  # Conservative fallback
                "recommended_mode": "stand_down",
                "confidence": 0.1
            }
    
    def _build_market_analysis_prompt(self, instrument: str, price_data: Dict[str, Any]) -> str:
        """Build structured prompt for market analysis"""
        return f"""
        Analyze {instrument} market structure:
        
        Current Price: {price_data.get('current_price')}
        24h High: {price_data.get('high_24h')}
        24h Low: {price_data.get('low_24h')}
        Volume: {price_data.get('volume')}
        ATR: {price_data.get('atr')}
        
        Technical Indicators:
        {json.dumps(price_data.get('indicators', {}), indent=2)}
        
        Identify:
        - Key support/resistance levels
        - Trend direction and strength
        - Breakout/breakdown probability
        - Confidence score (0.0-1.0)
        
        Return structured JSON response.
        """
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response and extract JSON"""
        try:
            # Try to find JSON in response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start != -1 and end != 0:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                # Fallback parsing for non-JSON responses
                return {"raw_response": response_text, "confidence": 0.3}
                
        except json.JSONDecodeError:
            return {"raw_response": response_text, "confidence": 0.1}
    
    def _fallback_analysis(self, instrument: str) -> Dict[str, Any]:
        """Fallback analysis when LLM fails"""
        return {
            "tier": "fallback",
            "instrument": instrument,
            "analysis": {
                "trend_direction": "neutral",
                "confidence": 0.1,
                "support_levels": [],
                "resistance_levels": []
            },
            "confidence": 0.1
        }

# Global LLM engine instance
llm_engine = OllamaLLMEngine()