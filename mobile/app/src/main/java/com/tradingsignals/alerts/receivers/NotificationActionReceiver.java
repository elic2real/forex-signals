package com.tradingsignals.alerts.receivers;

import android.app.NotificationManager;
import android.content.ActivityNotFoundException;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.util.Log;
import android.widget.Toast;

import com.tradingsignals.alerts.SignalDetailsActivity;

/**
 * Receiver for handling notification actions
 */
public class NotificationActionReceiver extends BroadcastReceiver {
    private static final String TAG = "NotificationActionReceiver";
    
    public static final String ACTION_MARK_AS_READ = "com.tradingsignals.alerts.MARK_AS_READ";
    public static final String ACTION_VIEW_SIGNAL = "com.tradingsignals.alerts.VIEW_SIGNAL";
    public static final String EXTRA_SIGNAL_ID = "signal_id";
    
    @Override
    public void onReceive(Context context, Intent intent) {
        String action = intent.getAction();
        String signalId = intent.getStringExtra(EXTRA_SIGNAL_ID);
        
        Log.d(TAG, "Received action: " + action + " for signal: " + signalId);
        
        if (ACTION_MARK_AS_READ.equals(action)) {
            handleMarkAsRead(context, signalId);
        } else if (ACTION_VIEW_SIGNAL.equals(action)) {
            handleViewSignal(context, signalId);
        }
    }
    
    private void handleMarkAsRead(Context context, String signalId) {
        // Mark signal as read in preferences or database
        Log.d(TAG, "Marking signal as read: " + signalId);
        
        // Store in SharedPreferences for now
        SharedPreferences prefs = context.getSharedPreferences("signal_prefs", Context.MODE_PRIVATE);
        prefs.edit().putBoolean("signal_read_" + signalId, true).apply();
        
        // Clear the notification with safe parsing
        NotificationManager notificationManager = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (notificationManager != null) {
            try {
                // Safe parsing with fallback
                int notificationId = parseIntWithFallback(signalId, 0);
                if (notificationId > 0) {
                    notificationManager.cancel(notificationId);
                } else {
                    // Fallback: cancel all notifications if parsing failed
                    notificationManager.cancelAll();
                    Log.d(TAG, "Cleared all notifications due to invalid signal ID: " + signalId);
                }
            } catch (Exception e) {
                Log.e(TAG, "Failed to cancel notification", e);
                // Final fallback: try to cancel all notifications
                try {
                    notificationManager.cancelAll();
                } catch (Exception fallbackException) {
                    Log.e(TAG, "Failed to cancel all notifications", fallbackException);
                }
            }
        }
    }
    
    private int parseIntWithFallback(String value, int fallback) {
        if (value == null || value.trim().isEmpty()) {
            return fallback;
        }
        try {
            return Integer.parseInt(value.trim());
        } catch (NumberFormatException e) {
            Log.w(TAG, "Failed to parse int: " + value + ", using fallback: " + fallback);
            return fallback;
        }
    }
    
    private void handleViewSignal(Context context, String signalId) {
        // Open signal details activity with comprehensive error handling
        Log.d(TAG, "Opening signal details for: " + signalId);
        
        try {
            // Validate signalId
            if (signalId == null || signalId.trim().isEmpty()) {
                Log.w(TAG, "Invalid signal ID, opening main activity instead");
                openMainActivity(context);
                return;
            }
            
            // Validate that target activity exists
            Intent intent = new Intent(context, SignalDetailsActivity.class);
            intent.putExtra("signal_id", signalId);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
            
            // Check if the activity can be resolved
            if (intent.resolveActivity(context.getPackageManager()) != null) {
                context.startActivity(intent);
                Log.d(TAG, "Successfully opened signal details for: " + signalId);
            } else {
                Log.w(TAG, "SignalDetailsActivity not found, opening main activity");
                openMainActivity(context);
            }
            
        } catch (ActivityNotFoundException e) {
            Log.e(TAG, "SignalDetailsActivity not found", e);
            openMainActivity(context);
        } catch (SecurityException e) {
            Log.e(TAG, "Permission denied to start activity", e);
            openMainActivity(context);
        } catch (Exception e) {
            Log.e(TAG, "Failed to open signal details", e);
            openMainActivity(context);
        }
    }
    
    private void openMainActivity(Context context) {
        try {
            // Use string-based intent to avoid compilation dependency issues
            Intent fallbackIntent = new Intent();
            fallbackIntent.setClassName(context, "com.tradingsignals.alerts.MainActivity");
            fallbackIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
            
            // Double-check that MainActivity exists
            if (fallbackIntent.resolveActivity(context.getPackageManager()) != null) {
                context.startActivity(fallbackIntent);
                Log.d(TAG, "Successfully opened main activity as fallback");
            } else {
                Log.e(TAG, "MainActivity not found - critical app error");
                // Show toast as last resort
                if (context instanceof android.app.Application) {
                    Toast.makeText(context, "App navigation error. Please restart the app.", Toast.LENGTH_LONG).show();
                }
            }
        } catch (Exception e) {
            Log.e(TAG, "Failed to open main activity fallback", e);
        }
    }
}
