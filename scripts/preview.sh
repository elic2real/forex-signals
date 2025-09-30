#!/usr/bin/env bash
# Preview script - creates shareable URL for testing

echo "🔗 Creating preview URL for Trading Signal Alerts..."

# Check if app is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ App not running. Start with 'make dev' first."
    exit 1
fi

echo "App is running locally on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""

# Try cloudflared tunnel first
if command -v cloudflared &> /dev/null; then
    echo "📡 Starting Cloudflare Tunnel..."
    cloudflared tunnel --url http://localhost:8000
elif command -v ngrok &> /dev/null; then
    echo "📡 Starting ngrok tunnel..."
    ngrok http 8000
else
    echo "📡 Starting localhost.run tunnel..."
    echo "Preview URL will appear below:"
    ssh -R 80:localhost:8000 nokey@localhost.run
fi
