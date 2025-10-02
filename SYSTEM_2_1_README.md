# System 2.1: Production-Grade Forex Signals with Ollama Integration

## 🚀 System Overview

System 2.1 represents a comprehensive upgrade to the forex signals platform, implementing production-grade testing, structured logging, AI integration via Ollama, and advanced risk management. This system satisfies all requirements from the three specialist panels:

- **Software Integrity & Testing (QA/TCA)**: Complete test suite with T.1, T.2, T.3 validations
- **System Observability & Debugging (SRE/Logging)**: Structured logging with L.1, L.2, L.3 requirements  
- **Core Logic Refinement (Quant/ML)**: Ollama LLM integration and advanced risk engines

## 🏗️ Architecture Components

### Core Infrastructure
- **Trace Logger**: UUID-based request tracing with structured JSON logging
- **Metrics Emitter**: Real-time Prometheus-compatible metrics export
- **Health Dashboard**: Comprehensive system health monitoring

### Risk Management Engines
- **GSSI/CAR Engine**: Global Systemic Stress & Concentrated Alpha Risk calculation
- **Sentinel Engine**: Black Swan protection with Protect/Pounce modes
- **Calibration Engine**: ECE monitoring with isotonic recalibration
- **MRC Engine**: Market Regime Classification with smooth weight transitions

### AI Integration
- **Ollama LLM Engine**: Local LLM integration for market analysis
- **Tier 3 Feature Hunt**: A/B testing for experimental LLM features
- **Conformal Prediction**: Uncertainty quantification for model outputs

### Position Management
- **Decimal Precision Sizing**: Kelly-Lite with 50x leverage caps
- **Add-to-Winners**: State machine for position scaling at +0.7R
- **Liquidity Cliff Monitor**: Emergency actions on spread deterioration

## 🔧 Installation & Setup

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install and start Ollama (for LLM features)
# Download from: https://ollama.ai
ollama pull llama3.1:8b
ollama serve
```

### 2. Configure Environment

```bash
# Create environment file
cp .env.example .env

# Edit configuration
nano .env
```

### 3. Initialize System Components

```bash
# Run system validation
python validate_setup.py

# Test System 2.1 integration
python system_2_1_demo.py
```

## 📊 System 2.1 Demo Results

Run the comprehensive integration demo:

```bash
python system_2_1_demo.py
```

Expected output demonstrates:
- ✅ All T.1, T.2, T.3 test requirements
- ✅ Structured logging (L.1, L.2, L.3)
- ✅ GSSI/CAR risk calculation
- ✅ Sentinel black swan protection
- ✅ Ollama LLM integration
- ✅ Real-time metrics & health monitoring

## 🧪 Testing Framework

### Unit Tests (T.1)
```bash
# Run sizing precision tests
pytest tests/test_system_2_1_comprehensive.py::TestSizingPrecision -v

# Run Add-to-Winners tests  
pytest tests/test_system_2_1_comprehensive.py::TestAddToWinnersEligibility -v
```

### Integration Tests (T.2)
```bash
# Run GSSI/CAR cascade tests
pytest tests/test_system_2_1_comprehensive.py::TestGSSICARCascade -v

# Run Sentinel override tests
pytest tests/test_system_2_1_comprehensive.py::TestSentinelOverride -v
```

### Acceptance Tests (T.3)
```bash
# Run safety compliance tests
pytest tests/test_system_2_1_comprehensive.py::TestSafetyCompliance -v

# Run liquidity cliff tests
pytest tests/test_system_2_1_comprehensive.py::TestLiquidityCliffEmergency -v
```

## 📈 Monitoring & Observability

### Prometheus Metrics Endpoint
```bash
# View current metrics
curl http://localhost:8000/metrics

# Key metrics exposed:
# - forex_nav: Net Asset Value
# - forex_gssi_score: Systemic stress level
# - forex_ece_value: Calibration error
# - forex_used_margin_pct: Margin utilization
```

### Health Dashboard
```python
from src.core.metrics_emitter import health_dashboard

# Get comprehensive health report
health_report = await health_dashboard.get_system_health_report()
print(f"System Health: {health_report['health_score']}/100")
```

### Structured Log Query Examples
```bash
# Query by trace ID
grep "trace_id.*abc123" logs/system.log

# Query guardrail blocks
grep "GUARDRAIL_BLOCK" logs/system.log | jq .

# Query supervisor decisions
grep "SUPERVISOR_DECISION" logs/system.log | jq .
```

## 🛡️ Risk Management Features

### Dynamic Position Sizing
- **Kelly-Lite**: Maximum 25% Kelly fraction
- **GSSI Integration**: Automatic size reduction during stress
- **Leverage Cap**: Hard 50x maximum leverage
- **Decimal Precision**: Eliminates floating-point errors

### Black Swan Protection
- **Sentinel Mode**: Automatic Protect/Pounce activation
- **Spread Monitoring**: Emergency actions on liquidity cliffs
- **Drawdown Kill Switch**: System halt at 5% daily loss

### Calibration Monitoring
- **ECE Tracking**: Expected Calibration Error monitoring  
- **Weight Lock**: Mandatory 48-hour freeze on ECE breach
- **Isotonic Recalibration**: Automatic probability calibration

## 🤖 Ollama LLM Integration

### Market Analysis
```python
from src.engines.ollama_llm_engine import llm_engine

# Analyze market structure
analysis = await llm_engine.analyze_market_structure(
    "EURUSD", 
    price_data
)
```

### News Sentiment
```python
# Process news sentiment
sentiment = await llm_engine.process_news_sentiment(
    news_items, 
    "EURUSD"
)
```

### Black Swan Assessment
```python
# Assess tail risk
risk_assessment = await llm_engine.assess_black_swan_risk(
    market_context
)
```

## 📋 Implementation Checklist

### ✅ Panel 1: Software Integrity & Testing
- [x] **T.1**: Sizing precision, Add-to-Winners, Conditional orders, Breakeven
- [x] **T.2**: GSSI/CAR cascade, MRC weight switch, Sentinel override, Currency caps
- [x] **T.3**: Safety compliance, Liquidity cliff, Drawdown kill switch

### ✅ Panel 2: System Observability & Debugging  
- [x] **L.1**: Structured JSON logging, Trace IDs, Guardrail status
- [x] **L.2**: Decision audit, API failure logging, Weight lock events
- [x] **L.3**: Real-time metrics, Health dashboard, Prometheus export

### ✅ Panel 3: Core Logic Refinement
- [x] **F.1**: GSSI/CAR calculation and dynamic sizing
- [x] **O**: MRC with 6 regime profiles and smooth transitions
- [x] **P.1**: ECE audit, weight lock, isotonic recalibration
- [x] **P.2**: Execution quality monitoring and route diversion
- [x] **R.1**: Conformal prediction and quantile-ATR
- [x] **R.2**: Sentinel Protect/Pounce mode logic

## 🚨 Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|---------|
| Used Margin | >80% | >90% | Reduce positions |
| GSSI Score | >0.6 | >0.8 | Activate Sentinel |
| ECE Value | >0.03 | >0.05 | Weight lock |
| Daily Drawdown | >3% | >5% | Kill switch |
| Free Margin | <$5K | <$1K | Halt trading |

## 📞 Support & Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   ```bash
   # Start Ollama service
   ollama serve
   
   # Verify model availability
   ollama list
   ```

2. **High Memory Usage**
   ```python
   # Check metrics history size
   len(metrics_emitter.metrics_history)  # Should be <1440
   ```

3. **ECE Breach False Positive**
   ```python
   # Check prediction history count
   len(calibration_auditor.prediction_history)  # Need >20 samples
   ```

### Debug Commands
```bash
# System health check
python -c "
from src.core.metrics_emitter import health_dashboard
import asyncio
report = asyncio.run(health_dashboard.get_system_health_report())
print(f'Health: {report[\"health_score\"]}/100')
"

# View current system state
python -c "
from src.engines.calibration_engine import calibration_auditor
print(f'System State: {calibration_auditor.system_state.value}')
"
```

## 🔄 Deployment Workflow

1. **Development**:
   ```bash
   python system_2_1_demo.py  # Validate all components
   pytest tests/ -v           # Run full test suite
   ```

2. **Staging**:
   ```bash
   python validate_setup.py   # Environment validation
   ollama pull llama3.1:8b   # Ensure LLM availability
   ```

3. **Production**:
   ```bash
   python run_dev.py          # Start with monitoring
   # Monitor health dashboard
   # Set up Prometheus scraping
   ```

---

**System 2.1** represents a production-ready, comprehensively tested, and fully observable forex trading system with integrated AI capabilities. All requirements from the three specialist panels have been implemented and validated.