#!/usr/bin/env bash
# Test script for trading signal alerts

echo "🧪 Running Trading Signal Tests..."

# Activate virtual environment
source .venv/bin/activate || .venv\Scripts\activate

# Run tests with coverage
pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

echo "📊 Coverage report generated in htmlcov/"
