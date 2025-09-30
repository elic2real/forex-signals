# Trading Signal Alerting System

A Python-based trading signal generator that sends push notifications to mobile devices instead of placing trades automatically.

## Features

- **Signal Generation**: Uses OANDA API for real-time market data and technical analysis
- **Mobile Alerts**: Sends push notifications via Firebase Cloud Messaging (FCM)
- **Risk Management**: Includes position sizing, risk assessment, and trade filtering
- **Technical Analysis**: Leverages pandas_ta for indicators (EMA, RSI, ADX, MACD, etc.)
- **Configuration-Driven**: YAML-based strategy and filter configuration

## Project Structure

```
signal-alerting-system/
├── src/
│   ├── signal_generator.py    # Main signal generation logic
│   ├── notification_sender.py # FCM push notification sender
│   ├── market_data.py         # OANDA API integration
│   ├── technical_analysis.py  # Technical indicators and filters
│   └── config_loader.py       # Configuration management
├── config/
│   ├── strategies.yaml        # Trading strategies configuration
│   └── firebase_config.json   # FCM configuration (add your own)
├── mobile_app/               # Android app template
│   └── README.md
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Add your OANDA API credentials
   - Add your Firebase server key

3. **Configure Strategies**
   - Edit `config/strategies.yaml` for your trading preferences
   - Set up FCM configuration in `config/firebase_config.json`

4. **Run Signal Generator**
   ```bash
   python src/signal_generator.py
   ```

## Mobile App Setup

See `mobile_app/README.md` for Android app setup instructions with FCM integration.

## Environment Variables

- `OANDA_API_KEY`: Your OANDA API access token
- `OANDA_ACCOUNT_ID`: Your OANDA account ID
- `OANDA_ENV`: `live` or `practice` (default: practice)
- `FCM_SERVER_KEY`: Firebase Cloud Messaging server key
