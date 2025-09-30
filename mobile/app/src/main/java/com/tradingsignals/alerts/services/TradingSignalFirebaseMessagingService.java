package com.tradingsignals.alerts.services;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import android.util.Log;

import androidx.core.app.NotificationCompat;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;
import com.google.gson.Gson;

import java.util.Map;

import com.tradingsignals.alerts.R;
import com.tradingsignals.alerts.SignalDetailsActivity;
import com.tradingsignals.alerts.models.TradingSignal;
import com.tradingsignals.alerts.receivers.NotificationActionReceiver;
import com.tradingsignals.alerts.utils.NotificationHelper;

public class TradingSignalFirebaseMessagingService extends FirebaseMessagingService {
    private static final String TAG = "FCMService";
    
    @Override
    public void onMessageReceived(RemoteMessage remoteMessage) {
        Log.d(TAG, "From: " + remoteMessage.getFrom());
        
        // Check if message contains a data payload
        if (remoteMessage.getData().size() > 0) {
            Log.d(TAG, "Message data payload: " + remoteMessage.getData());
            handleDataMessage(remoteMessage.getData());
        }
        
        // Check if message contains a notification payload
        if (remoteMessage.getNotification() != null) {
            Log.d(TAG, "Message Notification Body: " + remoteMessage.getNotification().getBody());
            handleNotificationMessage(remoteMessage);
        }
    }
    
    private void handleDataMessage(Map<String, String> data) {
        String messageType = data.get("type");
        
        if ("trading_signal".equals(messageType)) {
            handleTradingSignal(data);
        } else if ("signal_update".equals(messageType)) {
            handleSignalUpdate(data);
        } else if ("market_alert".equals(messageType)) {
            handleMarketAlert(data);
        } else {
            // Default notification
            showDefaultNotification(data);
        }
    }
    
    private void handleTradingSignal(Map<String, String> data) {
        try {
            // Parse signal data with comprehensive error handling
            String signalJson = data.get("signal_data");
            TradingSignal signal = null;
            
            if (signalJson != null && !signalJson.trim().isEmpty()) {
                try {
                    Gson gson = new Gson();
                    signal = gson.fromJson(signalJson, TradingSignal.class);
                } catch (Exception jsonException) {
                    Log.w(TAG, "Failed to parse signal JSON, using fallback", jsonException);
                    signal = null; // Will use fallback method
                }
            }
            
            if (signal == null) {
                // Fallback: create signal from individual fields with validation
                signal = new TradingSignal();
                
                // Safe string assignment
                signal.setInstrument(data.getOrDefault("instrument", "UNKNOWN"));
                signal.setSignalType(data.getOrDefault("signal_type", "UNKNOWN"));
                signal.setReason(data.getOrDefault("reason", "Technical analysis"));
                
                // Safe number parsing with fallbacks
                try {
                    String confidenceStr = data.getOrDefault("confidence", "0.0");
                    double confidence = parseDoubleWithFallback(confidenceStr, 0.0);
                    signal.setConfidence(confidence);
                } catch (Exception e) {
                    Log.w(TAG, "Failed to parse confidence, using default", e);
                    signal.setConfidence(0.0);
                }
                
                // Safe timestamp handling
                try {
                    String timestampStr = data.get("timestamp");
                    if (timestampStr != null && !timestampStr.isEmpty()) {
                        long timestamp = parseLongWithFallback(timestampStr, System.currentTimeMillis());
                        signal.setTimestamp(String.valueOf(timestamp));
                    } else {
                        signal.setTimestamp(String.valueOf(System.currentTimeMillis()));
                    }
                } catch (Exception e) {
                    Log.w(TAG, "Failed to parse timestamp, using current time", e);
                    signal.setTimestamp(String.valueOf(System.currentTimeMillis()));
                }
            }
            
            // Validate signal before showing notification
            if (isValidSignal(signal)) {
                showTradingSignalNotification(signal);
            } else {
                Log.w(TAG, "Invalid signal data, showing default notification");
                showDefaultNotification(data);
            }
            
        } catch (Exception e) {
            Log.e(TAG, "Error parsing trading signal", e);
            showDefaultNotification(data);
        }
    }
    
    private double parseDoubleWithFallback(String value, double fallback) {
        if (value == null || value.trim().isEmpty()) {
            return fallback;
        }
        try {
            return Double.parseDouble(value.trim());
        } catch (NumberFormatException e) {
            Log.w(TAG, "Failed to parse double: " + value + ", using fallback: " + fallback);
            return fallback;
        }
    }
    
    private long parseLongWithFallback(String value, long fallback) {
        if (value == null || value.trim().isEmpty()) {
            return fallback;
        }
        try {
            return Long.parseLong(value.trim());
        } catch (NumberFormatException e) {
            Log.w(TAG, "Failed to parse long: " + value + ", using fallback: " + fallback);
            return fallback;
        }
    }
    
    private boolean isValidSignal(TradingSignal signal) {
        return signal != null 
            && signal.getInstrument() != null 
            && !signal.getInstrument().equals("UNKNOWN")
            && signal.getSignalType() != null 
            && !signal.getSignalType().equals("UNKNOWN");
    }
    
    private void handleSignalUpdate(Map<String, String> data) {
        String signalId = data.get("signal_id");
        String updateType = data.get("update_type"); // "take_profit_hit", "stop_loss_hit", "expired"
        String instrument = data.get("instrument");
        
        showSignalUpdateNotification(signalId, updateType, instrument, data);
    }
    
    private void handleMarketAlert(Map<String, String> data) {
        String alertType = data.get("alert_type");
        String message = data.get("message");
        
        showMarketAlertNotification(alertType, message, data);
    }
    
    private void showTradingSignalNotification(TradingSignal signal) {
        NotificationHelper notificationHelper = new NotificationHelper(this);
        
        String title = String.format("%s Signal: %s", 
            signal.getSignalType(), signal.getInstrument());
        String body = String.format("Confidence: %s | %s", 
            signal.getFormattedConfidence(), 
            signal.getReason() != null ? signal.getReason() : "Technical analysis");
        
        // Create intent for signal details
        Intent intent = new Intent(this, SignalDetailsActivity.class);
        intent.putExtra("signal_id", signal.getId());
        intent.putExtra("signal_instrument", signal.getInstrument());
        intent.putExtra("signal_type", signal.getSignalType());
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);
        
        PendingIntent pendingIntent = PendingIntent.getActivity(
            this, 
            signal.getId().hashCode(), 
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );
        
        // Create action buttons
        Intent entryIntent = new Intent(this, NotificationActionReceiver.class);
        entryIntent.setAction("ACTION_ENTRY_TAKEN");
        entryIntent.putExtra("signal_id", signal.getId());
        PendingIntent entryPendingIntent = PendingIntent.getBroadcast(
            this, 
            signal.getId().hashCode() + 1, 
            entryIntent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );
        
        // Build notification
        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, NotificationHelper.CHANNEL_SIGNALS)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(body)
            .setStyle(new NotificationCompat.BigTextStyle()
                .bigText(buildDetailedSignalText(signal)))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_RECOMMENDATION)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .addAction(R.drawable.ic_check, "Entry Taken", entryPendingIntent)
            .setSound(RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION))
            .setVibrate(new long[]{0, 500, 250, 500});
        
        // Set color based on signal type
        if (signal.isBuySignal()) {
            builder.setColor(getResources().getColor(R.color.buy_color, null));
        } else {
            builder.setColor(getResources().getColor(R.color.sell_color, null));
        }
        
        NotificationManager notificationManager = getSystemService(NotificationManager.class);
        notificationManager.notify(signal.getId().hashCode(), builder.build());
        
        Log.d(TAG, "Trading signal notification shown for: " + signal.getInstrument());
    }
    
    private String buildDetailedSignalText(TradingSignal signal) {
        StringBuilder text = new StringBuilder();
        text.append("📈 ").append(signal.getInstrument()).append(" - ").append(signal.getSignalType()).append("\n");
        text.append("🎯 Confidence: ").append(signal.getFormattedConfidence()).append("\n");
        
        if (signal.getEntryPrice() > 0) {
            text.append("💰 Entry: ").append(signal.getFormattedPrice(signal.getEntryPrice())).append("\n");
        }
        if (signal.getStopLoss() > 0) {
            text.append("🛑 Stop Loss: ").append(signal.getFormattedPrice(signal.getStopLoss())).append("\n");
        }
        if (signal.getTakeProfit() > 0) {
            text.append("🎯 Take Profit: ").append(signal.getFormattedPrice(signal.getTakeProfit())).append("\n");
        }
        
        if (signal.getReason() != null) {
            text.append("📊 ").append(signal.getReason());
        }
        
        return text.toString();
    }
    
    private void showSignalUpdateNotification(String signalId, String updateType, String instrument, Map<String, String> data) {
        String title = "Signal Update: " + instrument;
        String body;
        
        switch (updateType) {
            case "take_profit_hit":
                title = "✅ Take Profit Hit!";
                body = String.format("%s signal closed with profit", instrument);
                break;
            case "stop_loss_hit":
                title = "❌ Stop Loss Hit";
                body = String.format("%s signal closed with loss", instrument);
                break;
            case "expired":
                title = "⏰ Signal Expired";
                body = String.format("%s signal has expired", instrument);
                break;
            default:
                body = String.format("%s signal updated", instrument);
        }
        
        showSimpleNotification(title, body, NotificationHelper.CHANNEL_UPDATES);
    }
    
    private void showMarketAlertNotification(String alertType, String message, Map<String, String> data) {
        String title = "Market Alert";
        
        if ("high_volatility".equals(alertType)) {
            title = "⚠️ High Volatility Alert";
        } else if ("market_news".equals(alertType)) {
            title = "📰 Market News";
        }
        
        showSimpleNotification(title, message, NotificationHelper.CHANNEL_ALERTS);
    }
    
    private void showDefaultNotification(Map<String, String> data) {
        String title = data.getOrDefault("title", "Trading Signals");
        String body = data.getOrDefault("body", "New trading signal available");
        
        showSimpleNotification(title, body, NotificationHelper.CHANNEL_GENERAL);
    }
    
    private void handleNotificationMessage(RemoteMessage remoteMessage) {
        RemoteMessage.Notification notification = remoteMessage.getNotification();
        String title = notification.getTitle();
        String body = notification.getBody();
        
        showSimpleNotification(title, body, NotificationHelper.CHANNEL_GENERAL);
    }
    
    private void showSimpleNotification(String title, String body, String channelId) {
        // Use string-based intent to avoid compilation dependency issues
        Intent intent = new Intent();
        intent.setClassName(this, "com.tradingsignals.alerts.MainActivity");
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);
        
        PendingIntent pendingIntent = PendingIntent.getActivity(
            this, 
            0, 
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );
        
        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, channelId)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(body)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setSound(RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION));
        
        NotificationManager notificationManager = getSystemService(NotificationManager.class);
        notificationManager.notify((title + body).hashCode(), builder.build());
    }
    
    @Override
    public void onNewToken(String token) {
        Log.d(TAG, "Refreshed token: " + token);
        
        // Send token to backend server
        sendTokenToServer(token);
        
        // Save token locally
        getSharedPreferences("app_prefs", MODE_PRIVATE)
            .edit()
            .putString("fcm_token", token)
            .apply();
    }
    
    private void sendTokenToServer(String token) {
        // Use ApiService to register the new token
        ApiService apiService = new ApiService(this);
        apiService.registerDevice(token, new ApiService.ApiCallback<String>() {
            @Override
            public void onSuccess(String response) {
                Log.d(TAG, "Token sent to server successfully: " + response);
            }
            
            @Override
            public void onError(String error) {
                Log.e(TAG, "Failed to send token to server: " + error);
            }
        });
    }
}
