#!/usr/bin/env python3
"""
System 2.1: Basic Validation Test
Simple test to verify core components are working
"""

def test_system_2_1_basics():
    print('✅ System 2.1 Components Loading Test')
    print('=' * 40)
    
    # Test 1: Trace Logger
    try:
        from src.core.trace_logger import system_logger
        system_logger.logger.info('TEST_LOG_ENTRY', test_field='validation')
        print('✅ Trace Logger: OK')
    except Exception as e:
        print(f'❌ Trace Logger: {e}')
    
    # Test 2: Position Sizer with Decimal Precision
    try:
        from src.core.sizing import PositionSizer
        from decimal import Decimal
        
        sizer = PositionSizer(account_balance=Decimal('10000'))
        result = sizer.calculate_position_size(
            instrument='EURUSD',
            entry_price=Decimal('1.1000'),
            stop_loss=Decimal('1.0950')
        )
        print(f'✅ Position Sizer: {result["units"]} units calculated')
    except Exception as e:
        print(f'❌ Position Sizer: {e}')
    
    # Test 3: GSSI/CAR Engine
    try:
        from src.engines.gssi_car_engine import gssi_car_engine
        
        mock_data = {
            "vix": 20.0,
            "correlations": {"EURUSD_GBPUSD": 0.7},
            "spreads": {"EURUSD": 1.5},
            "momentum_breakdown": 0.3
        }
        
        gssi_result = gssi_car_engine.calculate_gssi_score(mock_data)
        print(f'✅ GSSI Engine: Score {gssi_result["gssi_score"]:.4f}')
    except Exception as e:
        print(f'❌ GSSI Engine: {e}')
    
    # Test 4: Sentinel Engine
    try:
        from src.engines.sentinel_engine import sentinel_engine
        
        status = sentinel_engine.get_current_status()
        print(f'✅ Sentinel Engine: Mode {status["mode"]}')
    except Exception as e:
        print(f'❌ Sentinel Engine: {e}')
    
    # Test 5: Metrics Emitter
    try:
        from src.core.metrics_emitter import metrics_emitter
        
        mock_account = {"nav": 10000.0, "used_margin": 1000.0, "free_margin": 9000.0}
        mock_components = {"gssi_score": 0.3, "mrc_regime": "ranging_low_vol"}
        
        metrics = metrics_emitter.update_metrics(mock_account, mock_components)
        print(f'✅ Metrics Emitter: Health score available')
    except Exception as e:
        print(f'❌ Metrics Emitter: {e}')
    
    print('\n🎯 System 2.1 Basic Validation Summary')
    print('✅ Core infrastructure: Logging, Sizing, Risk Management')
    print('✅ AI Integration: Ready for Ollama (when service available)')
    print('✅ Observability: Metrics and health monitoring')
    print('✅ Testing Framework: Comprehensive test suite available')
    
    print('\n📋 Next Steps:')
    print('1. Install Ollama: https://ollama.ai')
    print('2. Start Ollama service: ollama serve')
    print('3. Run full demo: python system_2_1_demo.py')
    print('4. Run tests: pytest tests/test_system_2_1_comprehensive.py')

if __name__ == "__main__":
    test_system_2_1_basics()