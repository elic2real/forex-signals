# Forex Signals Production Checklist

## 1. Engines & Supervisor
- [ ] Engines 1–10 exist with `score()`, `init()`, `heartbeat()`.
- [ ] Supervisor Engine combines weights → outputs **final side, size, reason**.
- [ ] Engines are not “always returning 0” (heartbeat test ensures activity).

## 2. Risk & House Money
- [ ] House-Money allocation intact (base taper → profit-only → re-add).
- [ ] Position sizing capped by leverage = 50×.
- [ ] Anti-hedging enforced.
- [ ] No duplicate position sizes allowed.
- [ ] Trade bank = base + house logic, not full NAV.

## 3. Broker/OANDA Rules
- [ ] All orders submitted with server-side SL + TP.
- [ ] No multiple conditional triggers per order (Supervisor selects one).
- [ ] No duplicates of same size/direction.
- [ ] No opposite hedging positions.

## 4. Order Pipeline
- [ ] OANDA adapter uses idempotency keys to prevent double orders.
- [ ] Orders retry with exponential backoff.
- [ ] Shadow orders used for parity-check vs signals.
- [ ] Audit log includes order ID, units, SL/TP, reason.

## 5. Guardrails
- [ ] Daily drawdown stop (5% from peak NAV).
- [ ] Profit giveback guard (≥30% profit lost = stop).
- [ ] Loss streak cool-off (3 losses = pause 30m).
- [ ] Kill switch equity floor triggers flatten.

## 6. Exits
- [ ] Proximity exit (time-based, wait for price to retrace before closing).
- [ ] Velocity-aware exit (override TP if momentum strong).
- [ ] Range/threshold exits (daily, weekly, monthly highs/lows).
- [ ] Trailing stop & breakeven rules per strategy.

## 7. Journal & Calendar
- [ ] Journal auto-records trade reason + chart + metrics.
- [ ] Calendar tracks trades and outcomes daily/weekly/monthly.
- [ ] Narratives generated (“Entered EUR/USD long due to …”).
- [ ] Firebase sync tested across Web, Android, Desktop.

## 8. Debugging & Anti-Bug
- [ ] Config single-source-of-truth (`features.yaml`).
- [ ] Lint: black, ruff, eslint.
- [ ] Tests: unit, integration, shadow parity, canaries.
- [ ] Heartbeats confirm every engine runs.
- [ ] Canary tests prove every gate/guard triggers at least once.

## 9. Observability
- [ ] Structured logs (JSON with trace_id).
- [ ] Prometheus metrics: win%, expectancy, trade latency, gate block ratio.
- [ ] Hourly readiness score output.

## 10. Smoke-Test Script
- [ ] Place real order → verify SL/TP live on server.
- [ ] Trigger spread > 2 pips → blocked trade logged with reason.
- [ ] Force 3 losses → cool-off engaged.
- [ ] Shadow vs live orders match.
- [ ] Journal & calendar entries created.
