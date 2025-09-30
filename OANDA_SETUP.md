# OANDA API Setup Guide

## How to Get OANDA API Credentials

### Step 1: Create OANDA Account
1. Go to https://www.oanda.com/
2. Sign up for a **practice account** (free, no money required)
3. Verify your email address

### Step 2: Generate API Token
1. Log into your OANDA account
2. Go to **"Manage API Access"** in your account settings
3. Or directly visit: https://www.oanda.com/account/tpa/personal_token
4. Click **"Generate"** to create a new API token
5. **IMPORTANT:** Copy this token immediately - you can't see it again!

### Step 3: Get Account ID
1. In your OANDA dashboard, look for your **Account ID**
2. It will be in format like: `101-004-1234567-001`
3. Copy this Account ID

### Step 4: Update Environment File
Edit `.env` file and replace:
```
OANDA_API_KEY=your_actual_api_token_here
OANDA_ACCOUNT_ID=101-004-1234567-001
OANDA_ENV=practice
```

### Step 5: Test Connection
After updating credentials, restart the backend:
```bash
python run_dev.py
```

The backend will automatically switch from mock mode to real OANDA data!

## Environment Settings
- **practice**: Use OANDA's practice environment (recommended for testing)
- **live**: Use OANDA's live trading environment (real money - be careful!)

## Supported Currency Pairs
- EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CHF, USD/CAD
- And many more supported by OANDA

## Security Notes
- Never commit your real API key to version control
- Keep your `.env` file private
- Use practice environment for development/testing
- Only use live environment for actual trading