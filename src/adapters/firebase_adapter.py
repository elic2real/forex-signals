# Firebase adapter for journal and signal alerts
from typing import Dict, Any

import time
from typing import Dict, Any

class FirebaseAdapter:
    def __init__(self, service_account_path: str):
        self.service_account_path = service_account_path
        self.journal: list = []
        self.calendar: dict = {}

    def send_journal(self, entry: Dict[str, Any]):
        # Log trade reason, chart, metrics, narrative
        entry['timestamp'] = time.time()
        entry['narrative'] = self._generate_narrative(entry)
        self.journal.append(entry)
        print({"firebase": "journal_entry", "entry": entry})
        # Simulate Firebase sync
        return True

    def send_signal_alert(self, alert: Dict[str, Any]):
        # Log signal alert
        alert['timestamp'] = time.time()
        print({"firebase": "signal_alert", "alert": alert})
        return True

    def update_calendar(self, trade: Dict[str, Any]):
        # Track trades and outcomes daily/weekly/monthly
        from datetime import datetime
        dt = datetime.utcfromtimestamp(trade['timestamp'])
        day = dt.strftime('%Y-%m-%d')
        week = dt.strftime('%Y-W%U')
        month = dt.strftime('%Y-%m')
        for period, key in [("daily", day), ("weekly", week), ("monthly", month)]:
            self.calendar.setdefault(period, {})
            self.calendar[period].setdefault(key, []).append(trade)
        print({"firebase": "calendar_update", "trade": trade})
        return True

    def _generate_narrative(self, entry: Dict[str, Any]) -> str:
        # Generate narrative for journal
        pair = entry.get('pair', 'UNKNOWN')
        side = entry.get('side', 'UNKNOWN')
        reason = entry.get('reason', '')
        return f"Entered {pair} {side} due to {reason}"
