# FastAPI server with OpenAPI
from fastapi import FastAPI
from .routes import signals, trades, journal, health

app = FastAPI()
app.include_router(signals.router)
app.include_router(trades.router)
app.include_router(journal.router)
app.include_router(health.router)
