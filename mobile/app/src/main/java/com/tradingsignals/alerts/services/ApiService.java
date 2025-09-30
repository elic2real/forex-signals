package com.tradingsignals.alerts.services;

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.util.Log;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.io.IOException;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import com.tradingsignals.alerts.BuildConfig;
import com.tradingsignals.alerts.models.TradingSignal;

public class ApiService {
    private static final String TAG = "ApiService";
    
    // Production API configuration - Uses BuildConfig for environment-specific URLs
    private static final String PRODUCTION_DOMAIN = "api.forexalertpro.com"; // Replace with your domain
    private static final String PRODUCTION_URL = "https://" + PRODUCTION_DOMAIN;
    private static final String LOCALHOST_IP = "192.168.1.100"; // Keep for development
    private static final int DEFAULT_PORT = 8002;  // Updated to match backend
    private static final String DEV_BASE_URL = "http://" + LOCALHOST_IP + ":" + DEFAULT_PORT;
    
    // Use BuildConfig with fallback to prevent crashes
    private static final String BASE_URL = getBaseUrl();
    
    private static String getBaseUrl() {
        try {
            // Use BuildConfig value if available
            return BuildConfig.API_BASE_URL != null && !BuildConfig.API_BASE_URL.isEmpty() 
                ? BuildConfig.API_BASE_URL 
                : DEV_BASE_URL;
        } catch (Exception e) {
            // Fallback if BuildConfig is not available
            return DEV_BASE_URL;
        }
    }
    
    // Network timeouts
    private static final int CONNECT_TIMEOUT_SECONDS = 10;
    private static final int READ_TIMEOUT_SECONDS = 30;
    private static final int WRITE_TIMEOUT_SECONDS = 30;
    
    private final OkHttpClient client;
    private final Gson gson;
    private final Context context;
    private boolean isNetworkAvailable = true;
    
    public ApiService(Context context) {
        this.context = context;
        this.gson = new Gson();
        this.client = new OkHttpClient.Builder()
            .connectTimeout(CONNECT_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .readTimeout(READ_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .writeTimeout(WRITE_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(chain -> {
                // Add network availability check
                if (!isNetworkConnected()) {
                    throw new IOException("No network connection available");
                }
                return chain.proceed(chain.request());
            })
            .build();
    }
    
    private boolean isNetworkConnected() {
        try {
            ConnectivityManager connectivityManager = 
                (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
            if (connectivityManager != null) {
                NetworkInfo activeNetwork = connectivityManager.getActiveNetworkInfo();
                isNetworkAvailable = activeNetwork != null && activeNetwork.isConnectedOrConnecting();
                return isNetworkAvailable;
            }
        } catch (Exception e) {
            Log.e(TAG, "Failed to check network connectivity", e);
        }
        return false;
    }
    
    private void validateBaseUrl() throws IOException {
        if (BASE_URL == null || BASE_URL.isEmpty()) {
            throw new IOException("API base URL not configured");
        }
        if (!BASE_URL.startsWith("http")) {
            throw new IOException("Invalid API base URL format");
        }
    }
    
    public interface ApiCallback<T> {
        void onSuccess(T result);
        void onError(String error);
    }
    
    public void getSignals(ApiCallback<List<TradingSignal>> callback) {
        try {
            validateBaseUrl();
            
            Request request = new Request.Builder()
                .url(BASE_URL + "/api/signals")
                .get()
                .build();
            
            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    Log.e(TAG, "Failed to get signals", e);
                    String errorMessage;
                    if (e.getMessage() != null && e.getMessage().contains("No network")) {
                        errorMessage = "No internet connection. Please check your network.";
                    } else if (e.getMessage() != null && e.getMessage().contains("timeout")) {
                        errorMessage = "Connection timeout. Please try again.";
                    } else {
                        errorMessage = "Network error: " + e.getMessage();
                    }
                    callback.onError(errorMessage);
                }
                
                @Override
                public void onResponse(Call call, Response response) throws IOException {
                    try {
                        if (response.isSuccessful()) {
                            String responseBody = response.body() != null ? response.body().string() : "";
                            if (responseBody.isEmpty()) {
                                callback.onError("Empty response from server");
                                return;
                            }
                            
                            try {
                                Type listType = new TypeToken<List<TradingSignal>>(){}.getType();
                                List<TradingSignal> signals = gson.fromJson(responseBody, listType);
                                if (signals == null) {
                                    signals = new ArrayList<>(); // Return empty list instead of null
                                }
                                callback.onSuccess(signals);
                            } catch (Exception e) {
                                Log.e(TAG, "Failed to parse signals response", e);
                                callback.onError("Failed to parse server response");
                            }
                        } else {
                            Log.e(TAG, "Get signals failed: " + response.code());
                            String errorMessage = getHttpErrorMessage(response.code());
                            callback.onError(errorMessage);
                        }
                    } catch (Exception e) {
                        Log.e(TAG, "Unexpected error in response handling", e);
                        callback.onError("Unexpected error: " + e.getMessage());
                    } finally {
                        if (response.body() != null) {
                            response.body().close();
                        }
                    }
                }
            });
            
        } catch (Exception e) {
            Log.e(TAG, "Failed to initiate signals request", e);
            callback.onError("Failed to connect to server: " + e.getMessage());
        }
    }
    
    private String getHttpErrorMessage(int code) {
        switch (code) {
            case 400: return "Bad request. Please update the app.";
            case 401: return "Authentication failed. Please check settings.";
            case 403: return "Access denied. Contact support.";
            case 404: return "Service not found. Server may be down.";
            case 500: return "Server error. Please try again later.";
            case 503: return "Service unavailable. Please try again later.";
            default: return "Server error (" + code + "). Please try again.";
        }
    }
    
    public void getSignalById(String signalId, ApiCallback<TradingSignal> callback) {
        Request request = new Request.Builder()
            .url(BASE_URL + "/api/signals/" + signalId)
            .get()
            .build();
        
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e(TAG, "Failed to get signal by ID", e);
                callback.onError("Network error: " + e.getMessage());
            }
            
            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (response.isSuccessful()) {
                    String responseBody = response.body().string();
                    try {
                        TradingSignal signal = gson.fromJson(responseBody, TradingSignal.class);
                        callback.onSuccess(signal);
                    } catch (Exception e) {
                        Log.e(TAG, "Failed to parse signal response", e);
                        callback.onError("Failed to parse response");
                    }
                } else {
                    Log.e(TAG, "Get signal by ID failed: " + response.code());
                    callback.onError("Server error: " + response.code());
                }
                response.close();
            }
        });
    }
    
    public void registerDevice(String fcmToken, ApiCallback<String> callback) {
        try {
            String json = gson.toJson(new DeviceRegistration(fcmToken));
            RequestBody body = RequestBody.create(json, MediaType.get("application/json; charset=utf-8"));
            
            Request request = new Request.Builder()
                .url(BASE_URL + "/api/notifications/register")
                .post(body)
                .build();
            
            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    Log.e(TAG, "Failed to register device", e);
                    callback.onError("Network error: " + e.getMessage());
                }
                
                @Override
                public void onResponse(Call call, Response response) throws IOException {
                    if (response.isSuccessful()) {
                        String responseBody = response.body().string();
                        callback.onSuccess(responseBody);
                    } else {
                        Log.e(TAG, "Device registration failed: " + response.code());
                        callback.onError("Server error: " + response.code());
                    }
                    response.close();
                }
            });
        } catch (Exception e) {
            Log.e(TAG, "Failed to create registration request", e);
            callback.onError("Failed to create request");
        }
    }
    
    public void testNotification(ApiCallback<String> callback) {
        Request request = new Request.Builder()
            .url(BASE_URL + "/api/notifications/test")
            .post(RequestBody.create("", MediaType.get("application/json")))
            .build();
        
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e(TAG, "Failed to send test notification", e);
                callback.onError("Network error: " + e.getMessage());
            }
            
            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (response.isSuccessful()) {
                    String responseBody = response.body().string();
                    callback.onSuccess(responseBody);
                } else {
                    Log.e(TAG, "Test notification failed: " + response.code());
                    callback.onError("Server error: " + response.code());
                }
                response.close();
            }
        });
    }
    
    public void markSignalAction(String signalId, String action, ApiCallback<String> callback) {
        try {
            String json = gson.toJson(new SignalAction(signalId, action));
            RequestBody body = RequestBody.create(json, MediaType.get("application/json; charset=utf-8"));
            
            Request request = new Request.Builder()
                .url(BASE_URL + "/api/signals/" + signalId + "/action")
                .post(body)
                .build();
            
            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    Log.e(TAG, "Failed to mark signal action", e);
                    callback.onError("Network error: " + e.getMessage());
                }
                
                @Override
                public void onResponse(Call call, Response response) throws IOException {
                    if (response.isSuccessful()) {
                        String responseBody = response.body().string();
                        callback.onSuccess(responseBody);
                    } else {
                        Log.e(TAG, "Mark signal action failed: " + response.code());
                        callback.onError("Server error: " + response.code());
                    }
                    response.close();
                }
            });
        } catch (Exception e) {
            Log.e(TAG, "Failed to create signal action request", e);
            callback.onError("Failed to create request");
        }
    }
    
    public void checkHealth(ApiCallback<String> callback) {
        Request request = new Request.Builder()
            .url(BASE_URL + "/health")
            .get()
            .build();
        
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e(TAG, "Health check failed", e);
                callback.onError("Network error: " + e.getMessage());
            }
            
            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (response.isSuccessful()) {
                    String responseBody = response.body().string();
                    callback.onSuccess(responseBody);
                } else {
                    Log.e(TAG, "Health check failed: " + response.code());
                    callback.onError("Server error: " + response.code());
                }
                response.close();
            }
        });
    }
    
    // Helper classes for request bodies
    private static class DeviceRegistration {
        private final String fcm_token;
        @SuppressWarnings("unused") // Used by Gson for JSON serialization
        private final String device_type = "android";
        
        public DeviceRegistration(String fcmToken) {
            this.fcm_token = fcmToken;
        }
    }
    
    private static class SignalAction {
        @SuppressWarnings("unused") // Used by Gson for JSON serialization
        private final String signal_id;
        @SuppressWarnings("unused") // Used by Gson for JSON serialization
        private final String action;
        
        public SignalAction(String signalId, String action) {
            this.signal_id = signalId;
            this.action = action;
        }
    }
}
