# Trading Signal Alerts - Mobile App

## Overview

This Android application receives real-time forex trading signals from the backend server and displays them to users with push notifications. The app provides a clean, material design interface to view trading signals, their confidence levels, entry/exit points, and technical analysis.

## Features

### 📱 Core Functionality
- **Real-time Signal Display**: Live trading signals with confidence levels
- **Push Notifications**: Firebase Cloud Messaging for instant alerts
- **Signal Details**: Comprehensive view of entry, stop-loss, and take-profit levels
- **Technical Indicators**: ADX, RSI, EMA analysis display
- **Signal History**: Track all received signals and their status

### 🎨 User Interface
- **Material Design**: Modern, clean Android design
- **Signal Cards**: Easy-to-read trading signal cards
- **Color Coding**: Visual distinction between BUY/SELL signals
- **Confidence Indicators**: Visual confidence level representation
- **Swipe to Refresh**: Pull-to-refresh signal updates

### 🔔 Notification System
- **Instant Alerts**: FCM push notifications for new signals
- **Signal Updates**: Notifications for stop-loss/take-profit hits
- **Action Buttons**: Quick "Entry Taken" actions from notifications
- **Custom Channels**: Separate notification channels for different alert types

## Technical Architecture

### 📱 Android Components
```
com.tradingsignals.alerts/
├── MainActivity                    # Main signal list screen
├── SignalDetailsActivity          # Detailed signal view
├── SettingsActivity              # App configuration
├── models/
│   └── TradingSignal.java        # Data model for signals
├── services/
│   ├── ApiService.java           # Backend API communication
│   └── TradingSignalFirebaseMessagingService.java  # FCM handling
├── adapters/
│   └── SignalAdapter.java        # RecyclerView adapter
└── utils/
    └── NotificationHelper.java   # Notification channel management
```

### 🔗 Backend Integration
- **REST API**: OkHttp3 client for API communication
- **JSON Parsing**: Gson for signal data serialization
- **Real-time Updates**: Firebase Cloud Messaging
- **Device Registration**: Automatic FCM token registration

### 📊 Data Models
```java
TradingSignal {
    String id, instrument, signalType, status
    double confidence, entryPrice, stopLoss, takeProfit
    String timestamp, reason
    TechnicalIndicators indicators
}
```

## Setup Instructions

### 1. Prerequisites
- **Android Studio**: Latest version
- **Java**: JDK 8 or higher
- **Android SDK**: API level 24+ (Android 7.0)
- **Firebase Project**: For push notifications

### 2. Firebase Configuration
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create new project or select existing
3. Add Android app:
   - Package name: `com.tradingsignals.alerts`
   - App nickname: `Trading Signal Alerts`
4. Download `google-services.json`
5. Place file in `mobile/app/` directory
6. Enable Cloud Messaging in Firebase Console

### 3. Build Configuration
```bash
# Navigate to mobile directory
cd mobile/

# Build debug APK
./gradlew assembleDebug

# Install on connected device
./gradlew installDebug

# Build release APK (requires signing config)
./gradlew assembleRelease
```

### 4. Backend URL Configuration
Update the backend URL in `ApiService.java`:
```java
private static final String BASE_URL = "http://YOUR_SERVER_IP:8000";
```

## App Architecture

### 🏗️ Application Flow
1. **App Launch**: MainActivity loads recent signals
2. **FCM Registration**: Device registers for push notifications
3. **Signal Reception**: New signals trigger notifications
4. **User Interaction**: Tap notifications to view signal details
5. **Action Tracking**: Mark entry/exit actions for signals

### 📱 Screen Structure
```
MainActivity (Signal List)
├── SwipeRefreshLayout
│   └── RecyclerView (Signal Cards)
├── FloatingActionButton (Settings)
└── Toolbar (Refresh, Test Notification)

SignalDetailsActivity
├── Signal Information
├── Technical Indicators
├── Action Buttons
└── Share Options

SettingsActivity
├── Notification Preferences
├── Backend Configuration
└── App Information
```

### 🔔 Notification Channels
- **trading_signals**: High priority for new signals
- **signal_updates**: Default priority for status updates
- **market_alerts**: Low priority for market news
- **general**: System notifications

## API Integration

### 🌐 Backend Endpoints
```
GET /api/signals              # Fetch all signals
GET /api/signals/{id}         # Get specific signal
POST /api/notifications/register  # Register FCM token
POST /api/notifications/test  # Send test notification
POST /api/signals/{id}/action # Mark signal action
GET /health                   # Backend health check
```

### 📡 Request/Response Format
```json
// Signal Response
{
  "id": "signal_123",
  "instrument": "EUR_USD",
  "signal_type": "BUY",
  "confidence": 0.85,
  "entry_price": 1.08450,
  "stop_loss": 1.08200,
  "take_profit": 1.08750,
  "timestamp": "2025-09-21T15:30:00Z",
  "status": "ACTIVE",
  "reason": "ADX trending upward, RSI oversold recovery"
}
```

## Development Workflow

### 🛠️ Building for Development
1. **Connect Android Device** or start emulator
2. **Open Android Studio**
3. **Import Project**: Select `mobile/` directory
4. **Configure Firebase**: Add `google-services.json`
5. **Update Backend URL**: In `ApiService.java`
6. **Build & Run**: Click Run button or `Ctrl+R`

### 🔧 Testing
```bash
# Run unit tests
./gradlew test

# Run instrumented tests
./gradlew connectedAndroidTest

# Test notification functionality
# Use backend endpoint: POST /api/notifications/test
```

### 📱 Building for Production
1. **Create Signing Key**:
   ```bash
   keytool -genkey -v -keystore trading-signals.keystore -alias trading_signals -keyalg RSA -keysize 2048 -validity 10000
   ```

2. **Configure Signing** in `app/build.gradle`:
   ```gradle
   android {
       signingConfigs {
           release {
               keyAlias 'trading_signals'
               keyPassword 'your_password'
               storeFile file('trading-signals.keystore')
               storePassword 'your_password'
           }
       }
       buildTypes {
           release {
               signingConfig signingConfigs.release
               minifyEnabled true
               proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
           }
       }
   }
   ```

3. **Build Release APK**:
   ```bash
   ./gradlew assembleRelease
   ```

## Customization

### 🎨 UI Customization
- **Colors**: Modify `res/values/colors.xml`
- **Themes**: Update `res/values/themes.xml`
- **Layouts**: Customize XML layouts in `res/layout/`
- **Icons**: Replace drawable resources

### ⚙️ Configuration Options
- **Notification Settings**: Enable/disable notification types
- **Backend URL**: Dynamic server configuration
- **Refresh Intervals**: Customize data refresh rates
- **UI Preferences**: Theme, text size options

## Troubleshooting

### 🔍 Common Issues

1. **Notifications Not Working**:
   - Check `google-services.json` is present
   - Verify Firebase project configuration
   - Ensure device has network connectivity
   - Check notification permissions

2. **Backend Connection Failed**:
   - Verify backend server is running
   - Check IP address in `ApiService.java`
   - Ensure device can reach backend network
   - Test with `/health` endpoint

3. **Build Errors**:
   - Clean and rebuild project
   - Check Gradle sync status
   - Verify Android SDK installation
   - Update dependencies if needed

### 📱 Device Requirements
- **Android Version**: 7.0+ (API level 24)
- **RAM**: 2GB minimum
- **Storage**: 100MB for app installation
- **Network**: Internet connection required
- **Permissions**: Notification access

## Performance Optimization

### ⚡ App Performance
- **RecyclerView**: Efficient list rendering with ViewHolder pattern
- **Image Loading**: Glide for optimized image caching
- **Network**: OkHttp connection pooling and caching
- **Background Tasks**: WorkManager for reliable background operations

### 🔋 Battery Optimization
- **Doze Mode**: Compatible with Android battery optimization
- **Background Limits**: Efficient FCM usage
- **Network Usage**: Minimal API calls with caching
- **CPU Usage**: Optimized UI updates and data processing

## Future Enhancements

### 🚀 Planned Features
- **Signal Analytics**: Performance tracking and statistics
- **Custom Alerts**: User-defined notification criteria
- **Signal Sharing**: Export and share signal information
- **Dark Mode**: Full dark theme support
- **Widget Support**: Home screen signal widgets
- **Offline Mode**: Basic functionality without network

### 🔧 Technical Improvements
- **Kotlin Migration**: Convert Java to Kotlin
- **Architecture Components**: ViewModel, LiveData, Room
- **Dependency Injection**: Dagger/Hilt implementation
- **Testing**: Increased test coverage
- **Security**: Enhanced encryption and secure storage

## License

This project is part of the Trading Signal Alerts system. See the main project README for licensing information.
#   f o r e x - s i g n a l s  
 