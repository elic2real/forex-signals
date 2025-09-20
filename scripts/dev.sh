#!/usr/bin/env bash
# Development script for trading signal alerts

echo "🚀 Starting Trading Signal Alerts Backend..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate || .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your API keys before running again."
    exit 1
fi

# Start the FastAPI server
echo "Starting FastAPI server on http://localhost:8000"
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
