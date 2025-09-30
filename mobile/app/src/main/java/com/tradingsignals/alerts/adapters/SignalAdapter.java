package com.tradingsignals.alerts.adapters;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.RecyclerView;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

import com.tradingsignals.alerts.R;
import com.tradingsignals.alerts.models.TradingSignal;

public class SignalAdapter extends RecyclerView.Adapter<SignalAdapter.SignalViewHolder> {
    
    private final List<TradingSignal> signals;
    private final OnSignalClickListener clickListener;
    private final SimpleDateFormat timeFormat;
    
    public interface OnSignalClickListener {
        void onSignalClick(TradingSignal signal);
    }
    
    public SignalAdapter(List<TradingSignal> signals, OnSignalClickListener clickListener) {
        this.signals = signals;
        this.clickListener = clickListener;
        this.timeFormat = new SimpleDateFormat("HH:mm", Locale.getDefault());
    }
    
    @NonNull
    @Override
    public SignalViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_signal, parent, false);
        return new SignalViewHolder(view);
    }
    
    @Override
    public void onBindViewHolder(@NonNull SignalViewHolder holder, int position) {
        TradingSignal signal = signals.get(position);
        holder.bind(signal);
    }
    
    @Override
    public int getItemCount() {
        return signals.size();
    }
    
    public class SignalViewHolder extends RecyclerView.ViewHolder {
        private final TextView textViewInstrument;
        private final TextView textViewSignalType;
        private final TextView textViewConfidence;
        private final TextView textViewStatus;
        private final TextView textViewEntryPrice;
        private final TextView textViewStopLoss;
        private final TextView textViewTakeProfit;
        private final TextView textViewReason;
        private final TextView textViewTimestamp;
        
        public SignalViewHolder(@NonNull View itemView) {
            super(itemView);
            
            textViewInstrument = itemView.findViewById(R.id.textViewInstrument);
            textViewSignalType = itemView.findViewById(R.id.textViewSignalType);
            textViewConfidence = itemView.findViewById(R.id.textViewConfidence);
            textViewStatus = itemView.findViewById(R.id.textViewStatus);
            textViewEntryPrice = itemView.findViewById(R.id.textViewEntryPrice);
            textViewStopLoss = itemView.findViewById(R.id.textViewStopLoss);
            textViewTakeProfit = itemView.findViewById(R.id.textViewTakeProfit);
            textViewReason = itemView.findViewById(R.id.textViewReason);
            textViewTimestamp = itemView.findViewById(R.id.textViewTimestamp);
            
            itemView.setOnClickListener(v -> {
                int position = getAdapterPosition();
                if (position != RecyclerView.NO_POSITION && clickListener != null) {
                    clickListener.onSignalClick(signals.get(position));
                }
            });
        }
        
        public void bind(TradingSignal signal) {
            Context context = itemView.getContext();
            
            // Basic signal information
            textViewInstrument.setText(signal.getInstrument());
            textViewSignalType.setText(signal.getSignalType());
            textViewConfidence.setText(context.getString(R.string.confidence_label, signal.getFormattedConfidence()));
            textViewStatus.setText(signal.getStatus());
            
            // Price information
            if (signal.getEntryPrice() > 0) {
                textViewEntryPrice.setText(signal.getFormattedPrice(signal.getEntryPrice()));
            } else {
                textViewEntryPrice.setText("-");
            }
            
            if (signal.getStopLoss() > 0) {
                textViewStopLoss.setText(signal.getFormattedPrice(signal.getStopLoss()));
            } else {
                textViewStopLoss.setText("-");
            }
            
            if (signal.getTakeProfit() > 0) {
                textViewTakeProfit.setText(signal.getFormattedPrice(signal.getTakeProfit()));
            } else {
                textViewTakeProfit.setText("-");
            }
            
            // Reason
            if (signal.getReason() != null && !signal.getReason().isEmpty()) {
                textViewReason.setText(signal.getReason());
                textViewReason.setVisibility(View.VISIBLE);
            } else {
                textViewReason.setVisibility(View.GONE);
            }
            
            // Timestamp
            textViewTimestamp.setText(formatTimestamp(signal.getTimestamp()));
            
            // Set colors based on signal type
            int signalTypeColor;
            int signalTypeBackground;
            if (signal.isBuySignal()) {
                signalTypeColor = ContextCompat.getColor(context, R.color.white);
                signalTypeBackground = R.drawable.buy_signal_background;
            } else {
                signalTypeColor = ContextCompat.getColor(context, R.color.white);
                signalTypeBackground = R.drawable.sell_signal_background;
            }
            
            textViewSignalType.setTextColor(signalTypeColor);
            textViewSignalType.setBackgroundResource(signalTypeBackground);
            
            // Set status color
            int statusColor;
            switch (signal.getStatus().toUpperCase()) {
                case "ACTIVE":
                    statusColor = ContextCompat.getColor(context, R.color.status_active);
                    break;
                case "CLOSED":
                    statusColor = ContextCompat.getColor(context, R.color.status_closed);
                    break;
                case "EXPIRED":
                    statusColor = ContextCompat.getColor(context, R.color.status_expired);
                    break;
                default:
                    statusColor = ContextCompat.getColor(context, R.color.neutral_color);
            }
            textViewStatus.setTextColor(statusColor);
            
            // Set confidence color
            int confidenceColor;
            String confidenceLevel = signal.getConfidenceLevel();
            switch (confidenceLevel) {
                case "HIGH":
                    confidenceColor = ContextCompat.getColor(context, R.color.confidence_high);
                    break;
                case "MEDIUM":
                    confidenceColor = ContextCompat.getColor(context, R.color.confidence_medium);
                    break;
                case "LOW":
                    confidenceColor = ContextCompat.getColor(context, R.color.confidence_low);
                    break;
                default:
                    confidenceColor = ContextCompat.getColor(context, R.color.text_secondary);
            }
            
            // Create a subtle confidence indicator
            textViewConfidence.setTextColor(confidenceColor);
        }
        
        private String formatTimestamp(String timestamp) {
            try {
                // For now, just show relative time
                // You can implement proper timestamp parsing based on your backend format
                if (timestamp == null || timestamp.isEmpty()) {
                    return "Unknown time";
                }
                
                // Simple relative time formatting
                // In a real app, you'd parse the ISO timestamp and calculate the difference
                return "A few minutes ago";
                
            } catch (Exception e) {
                return "Unknown time";
            }
        }
    }
}
