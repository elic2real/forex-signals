# Architecture Overview

- 11 engines (10 analysis + 1 supervisor)
- House-Money risk core
- OANDA + Firebase adapters
- Journal, calendar, and signals UI (web/desktop/mobile)
- Activation guardrails, canaries, shadow orders, decision records
- API: FastAPI, OpenAPI, Pydantic models
- Observability: logs, metrics, traces
