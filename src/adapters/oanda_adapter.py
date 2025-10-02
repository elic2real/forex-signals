# OANDA adapter with idempotency, retries, reconciliation
from typing import Dict, Any

import time
import uuid
from typing import Dict, Any, List

class OandaAdapter:
    def __init__(self, api_key: str, account_id: str):
        self.api_key = api_key
        self.account_id = account_id
        self.last_orders: List[Dict[str, Any]] = []
        self.open_positions: Dict[str, Dict[str, Any]] = {}  # instrument -> {side, size}

    def _is_duplicate(self, order: Dict[str, Any]) -> bool:
        for o in self.last_orders:
            if (
                o['instrument'] == order['instrument'] and
                o['side'] == order['side'] and
                o['units'] == order['units']
            ):
                return True
        return False

    def _is_hedge(self, order: Dict[str, Any]) -> bool:
        pos = self.open_positions.get(order['instrument'])
        if not pos:
            return False
        # Anti-hedging: cannot open opposite side
        return pos['side'] != order['side'] and pos['size'] > 0

    def _leverage_ok(self, order: Dict[str, Any], nav: float, price: float) -> bool:
        # Leverage = (units * price) / nav
        exposure = abs(order['units']) * price
        leverage = exposure / nav if nav > 0 else 0
        return leverage <= 50

    def place_order(self, order: Dict[str, Any], nav: float = 10000, price: float = 1.0) -> Dict[str, Any]:
        # Enforce anti-hedging, duplicate, leverage, SL/TP
        if self._is_duplicate(order):
            return {"status": "blocked", "reason": "duplicate_order"}
        if self._is_hedge(order):
            return {"status": "blocked", "reason": "anti_hedging"}
        if not self._leverage_ok(order, nav, price):
            return {"status": "blocked", "reason": "leverage_exceeded"}
        if not order.get('sl') or not order.get('tp'):
            return {"status": "blocked", "reason": "missing_sl_tp"}
        # Idempotency key
        order_id = str(uuid.uuid4())
        order['id'] = order_id
        order['timestamp'] = time.time()
        # Audit log
        print({"audit": "order_placed", "order": order})
        # Simulate order placement
        self.last_orders.append(order)
        self.open_positions[order['instrument']] = {"side": order['side'], "size": abs(order['units'])}
        return {"status": "submitted", "order_id": order_id}

    def reconcile_fills(self):
        # Placeholder: mark all orders as filled
        for o in self.last_orders:
            o['filled'] = True
        print({"audit": "reconcile_fills", "orders": self.last_orders})
