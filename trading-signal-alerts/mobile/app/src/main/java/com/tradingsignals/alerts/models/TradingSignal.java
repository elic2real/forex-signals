package com.tradingsignals.alerts.models;

import static java.lang.String.*;

import android.annotation.SuppressLint;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;
import java.util.Date;

public class TradingSignal implements Serializable {
    @SerializedName("id")
    private String id;
    
    @SerializedName("instrument")
    private String instrument;
    
    @SerializedName("signal_type")
    private String signalType; // "BUY" or "SELL"
    
    @SerializedName("confidence")
    private double confidence;
    
    @SerializedName("entry_price")
    private double entryPrice;
    
    @SerializedName("stop_loss")
    private double stopLoss;
    
    @SerializedName("take_profit")
    private double takeProfit;
    
    @SerializedName("current_price")
    private double currentPrice;
    
    @SerializedName("spread")
    private double spread;
    
    @SerializedName("timestamp")
    private String timestamp;
    
    @SerializedName("status")
    private String status; // "ACTIVE", "CLOSED", "EXPIRED"
    
    @SerializedName("reason")
    private String reason;
    
    @SerializedName("indicators")
    private TechnicalIndicators indicators;
    
    // Constructors
    public TradingSignal() {}
    
    public TradingSignal(String id, String instrument, String signalType, double confidence) {
        this.id = id;
        this.instrument = instrument;
        this.signalType = signalType;
        this.confidence = confidence;
        this.status = "ACTIVE";
    }
    
    // Getters and Setters
    public String getId() {
        return id;
    }
    
    public void setId(String id) {
        this.id = id;
    }
    
    public String getInstrument() {
        return instrument;
    }
    
    public void setInstrument(String instrument) {
        this.instrument = instrument;
    }
    
    public String getSignalType() {
        return signalType;
    }
    
    public void setSignalType(String signalType) {
        this.signalType = signalType;
    }
    
    public double getConfidence() {
        return confidence;
    }
    
    public void setConfidence(double confidence) {
        this.confidence = confidence;
    }
    
    public double getEntryPrice() {
        return entryPrice;
    }
    
    public void setEntryPrice(double entryPrice) {
        this.entryPrice = entryPrice;
    }
    
    public double getStopLoss() {
        return stopLoss;
    }
    
    public void setStopLoss(double stopLoss) {
        this.stopLoss = stopLoss;
    }
    
    public double getTakeProfit() {
        return takeProfit;
    }
    
    public void setTakeProfit(double takeProfit) {
        this.takeProfit = takeProfit;
    }
    
    public double getCurrentPrice() {
        return currentPrice;
    }
    
    public void setCurrentPrice(double currentPrice) {
        this.currentPrice = currentPrice;
    }
    
    public double getSpread() {
        return spread;
    }
    
    public void setSpread(double spread) {
        this.spread = spread;
    }
    
    public String getTimestamp() {
        return timestamp;
    }
    
    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }
    
    public String getStatus() {
        return status;
    }
    
    public void setStatus(String status) {
        this.status = status;
    }
    
    public String getReason() {
        return reason;
    }
    
    public void setReason(String reason) {
        this.reason = reason;
    }
    
    public TechnicalIndicators getIndicators() {
        return indicators;
    }
    
    public void setIndicators(TechnicalIndicators indicators) {
        this.indicators = indicators;
    }
    
    // Helper methods
    public boolean isBuySignal() {
        return "BUY".equalsIgnoreCase(signalType);
    }
    
    public boolean isSellSignal() {
        return "SELL".equalsIgnoreCase(signalType);
    }
    
    public boolean isActive() {
        return "ACTIVE".equalsIgnoreCase(status);
    }
    
    public String getConfidenceLevel() {
        if (confidence >= 0.8) return "HIGH";
        if (confidence >= 0.6) return "MEDIUM";
        return "LOW";
    }
    
    @SuppressLint("DefaultLocale")
    public String getFormattedPrice(double price) {
        return format("%.5f", price);
    }
    
    @SuppressLint("DefaultLocale")
    public String getFormattedConfidence() {
        String format = format("%.1f%%", confidence * 100);
        return format;
    }
    
    // Technical Indicators inner class
    public static class TechnicalIndicators {
        @SerializedName("adx")
        private double adx;
        
        @SerializedName("rsi")
        private double rsi;
        
        @SerializedName("ema_20")
        private double ema20;
        
        @SerializedName("ema_50")
        private double ema50;
        
        @SerializedName("macd")
        private double macd;
        
        @SerializedName("macd_signal")
        private double macdSignal;
        
        // Constructors
        public TechnicalIndicators() {}
        
        // Getters and Setters
        public double getAdx() {
            return adx;
        }
        
        public void setAdx(double adx) {
            this.adx = adx;
        }
        
        public double getRsi() {
            return rsi;
        }
        
        public void setRsi(double rsi) {
            this.rsi = rsi;
        }
        
        public double getEma20() {
            return ema20;
        }
        
        public void setEma20(double ema20) {
            this.ema20 = ema20;
        }
        
        public double getEma50() {
            return ema50;
        }
        
        public void setEma50(double ema50) {
            this.ema50 = ema50;
        }
        
        public double getMacd() {
            return macd;
        }
        
        public void setMacd(double macd) {
            this.macd = macd;
        }
        
        public double getMacdSignal() {
            return macdSignal;
        }
        
        public void setMacdSignal(double macdSignal) {
            this.macdSignal = macdSignal;
        }
        
        // Helper methods
        public String getAdxStrength() {
            if (adx >= 50) return "VERY STRONG";
            if (adx >= 25) return "STRONG";
            if (adx >= 20) return "MODERATE";
            return "WEAK";
        }
        
        public String getRsiLevel() {
            if (rsi >= 70) return "OVERBOUGHT";
            if (rsi <= 30) return "OVERSOLD";
            return "NEUTRAL";
        }
    }
}
