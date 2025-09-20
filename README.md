# Trading Signal Alerts

Built with RapidShip methodology - Real-time OANDA trading signals via mobile push notifications.

## 🚀 Quick Start

```bash
# Development
make dev          # Start signal backend
make test         # Run tests
make preview      # Get shareable URL

# Mobile App
cd mobile/        # Android app with FCM
./gradlew build   # Build APK

# Deployment
make ship         # Deploy to production
make logs         # View live logs
make rollback     # Revert last deploy
```

## 📁 Project Structure

```
.
├── src/              # FastAPI backend (signal generation)
│   ├── api/          # REST endpoints
│   ├── core/         # Configuration, logging
│   ├── services/     # OANDA API, FCM, signal logic
│   └── models/       # Data models
├── mobile/           # Android app
│   ├── app/          # Main app module
│   └── gradle/       # Build configuration
├── tests/            # Test suite
├── scripts/          # Automation scripts
├── .devcontainer/    # VS Code dev container
├── .github/          # GitHub Actions
├── docker-compose.yml # Local services
├── Makefile          # Command interface
└── README.md         # You are here
```

## 🔧 Configuration

Environment variables:
- `OANDA_API_KEY` - OANDA API key
- `OANDA_ACCOUNT_ID` - OANDA account ID
- `OANDA_ENV` - live or practice
- `FIREBASE_PROJECT_ID` - Firebase project ID
- `FIREBASE_PRIVATE_KEY` - Firebase service account key
- `LOG_LEVEL` - Logging verbosity (DEBUG|INFO|WARN|ERROR)

## 📊 Signal Flow

```
OANDA Market Data → Technical Analysis → Signal Decision → FCM Push → Mobile Alert
```

## 🎯 Signal Logic

Extracted from proven trading bot:
- **Technical Indicators**: ADX, RSI, EMA crossovers
- **Risk Filters**: Spread, correlation, volatility
- **Timing**: Session boundaries, weekend blocks
- **Confirmation**: Multiple timeframe analysis

## 📱 Mobile Features

- Real-time push notifications
- Signal history
- Instrument tracking
- Alert preferences

## 🚢 Deployment

This project auto-deploys:
- `main` → production (Fly.io)
- `develop` → staging

## 🔐 Firebase Setup

1. Create Firebase project at https://console.firebase.google.com
2. Enable Cloud Messaging
3. Download service account key
4. Add Android app with SHA fingerprint

## 📝 License

MIT

---
*Generated with RapidShip methodology for rapid trading signal deployment*
