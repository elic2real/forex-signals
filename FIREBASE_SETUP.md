# Firebase Setup Guide for Trading Signal Alerts

## Step-by-Step Firebase Configuration

### 1. 🌐 Create Firebase Project

1. **Go to Firebase Console**: https://console.firebase.google.com/
2. **Click "Create a project"**
3. **Project Details**:
   - Project name: `Trading Signal Alerts`
   - Project ID: `trading-signal-alerts-xxxxx` (Firebase will generate unique ID)
   - Click "Continue"

4. **Google Analytics** (Optional but recommended):
   - Enable Google Analytics: `Yes`
   - Analytics location: `Your Country`
   - Data sharing settings: Accept defaults
   - Click "Create project"

5. **Wait for project creation** (1-2 minutes)

### 2. 📱 Add Android App

1. **In Firebase Console**, click "Add app" → Android icon
2. **Register Android App**:
   - Android package name: `com.tradingsignals.alerts`
   - App nickname: `Trading Signal Alerts`
   - Debug signing certificate SHA-1: (Leave empty for now)
   - Click "Register app"

3. **Download config file**:
   - Download `google-services.json`
   - **IMPORTANT**: Save this file - you'll need it!

### 3. 🔔 Enable Cloud Messaging

1. **In Firebase Console**, go to your project
2. **Left sidebar** → "Cloud Messaging"
3. **Cloud Messaging API**:
   - Click "Enable" if not already enabled
   - Note down your "Server key" (for backend integration)

### 4. 📋 Get Required Information

After setup, you'll have:
- ✅ `google-services.json` file
- ✅ Firebase project ID
- ✅ Cloud Messaging Server Key

## Quick Setup Commands

Once you have `google-services.json`:

```bash
# Copy google-services.json to mobile app
cp /path/to/downloaded/google-services.json "C:/Users/mawil/oandabot2/signal forex/trading-signal-alerts/mobile/app/"

# Verify file is in correct location
ls "C:/Users/mawil/oandabot2/signal forex/trading-signal-alerts/mobile/app/google-services.json"
```

## Firebase Console URLs

- **Main Console**: https://console.firebase.google.com/
- **Your Project**: https://console.firebase.google.com/project/YOUR_PROJECT_ID
- **Cloud Messaging**: https://console.firebase.google.com/project/YOUR_PROJECT_ID/messaging

## Next Steps After Firebase Setup

1. ✅ Download and place `google-services.json`
2. ✅ Note Firebase Server Key for backend
3. ✅ Test mobile app build
4. ✅ Test push notifications
