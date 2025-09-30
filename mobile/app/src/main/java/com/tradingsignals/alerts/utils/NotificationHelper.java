package com.tradingsignals.alerts.utils;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Context;
import android.os.Build;

import com.tradingsignals.alerts.R;

public class NotificationHelper {
    public static final String CHANNEL_SIGNALS = "trading_signals";
    public static final String CHANNEL_UPDATES = "signal_updates";
    public static final String CHANNEL_ALERTS = "market_alerts";
    public static final String CHANNEL_GENERAL = "general";
    
    private final Context context;
    private final NotificationManager notificationManager;
    
    public NotificationHelper(Context context) {
        this.context = context;
        this.notificationManager = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
    }
    
    public void createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            createSignalsChannel();
            createUpdatesChannel();
            createAlertsChannel();
            createGeneralChannel();
        }
    }
    
    private void createSignalsChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_SIGNALS,
                context.getString(R.string.notification_channel_signals),
                NotificationManager.IMPORTANCE_HIGH  // High priority for trading signals
            );
            channel.setDescription(context.getString(R.string.notification_channel_signals_description));
            channel.enableVibration(true);
            channel.setVibrationPattern(new long[]{0, 500, 250, 500}); // Distinctive pattern
            channel.setShowBadge(true);
            channel.enableLights(true);
            channel.setLockscreenVisibility(android.app.Notification.VISIBILITY_PUBLIC);
            
            notificationManager.createNotificationChannel(channel);
        }
    }
    
    private void createUpdatesChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_UPDATES,
                context.getString(R.string.notification_channel_updates),
                NotificationManager.IMPORTANCE_DEFAULT
            );
            channel.setDescription(context.getString(R.string.notification_channel_updates_description));
            channel.enableVibration(true);
            channel.setShowBadge(true);
            
            notificationManager.createNotificationChannel(channel);
        }
    }
    
    private void createAlertsChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_ALERTS,
                context.getString(R.string.notification_channel_alerts),
                NotificationManager.IMPORTANCE_DEFAULT
            );
            channel.setDescription(context.getString(R.string.notification_channel_alerts_description));
            channel.enableVibration(false);
            channel.setShowBadge(false);
            
            notificationManager.createNotificationChannel(channel);
        }
    }
    
    private void createGeneralChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_GENERAL,
                context.getString(R.string.notification_channel_general),
                NotificationManager.IMPORTANCE_LOW
            );
            channel.setDescription(context.getString(R.string.notification_channel_general_description));
            channel.enableVibration(false);
            channel.setShowBadge(false);
            
            notificationManager.createNotificationChannel(channel);
        }
    }
}
