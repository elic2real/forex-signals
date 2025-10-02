from src.adapters.oanda_adapter import OandaAdapter
from src.adapters.firebase_adapter import FirebaseAdapter

def test_oanda_adapter_contract(oanda_order):
    adapter = OandaAdapter(api_key='test', account_id='test')
    result = adapter.place_order(oanda_order)
    assert isinstance(result, dict)
    assert 'status' in result

def test_firebase_adapter_contract(firebase_entry):
    adapter = FirebaseAdapter(service_account_path='dummy.json')
    # Should not raise
    adapter.send_journal(firebase_entry)
    adapter.send_signal_alert(firebase_entry)
