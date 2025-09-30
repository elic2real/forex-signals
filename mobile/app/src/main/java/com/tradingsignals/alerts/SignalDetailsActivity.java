package com.tradingsignals.alerts;

import android.os.Bundle;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

public class SignalDetailsActivity extends AppCompatActivity {
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_signal_details);
        
        // Get signal data from intent
        String signalId = getIntent().getStringExtra("signal_id");
        String instrument = getIntent().getStringExtra("signal_instrument");
        String signalType = getIntent().getStringExtra("signal_type");
        
        // Set up toolbar
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setTitle("Signal Details");
        }
        
        // Display signal information
        TextView titleView = findViewById(R.id.textViewDetailTitle);
        titleView.setText(instrument + " - " + signalType);
    }
    
    @Override
    public boolean onSupportNavigateUp() {
        onBackPressed();
        return true;
    }
}
