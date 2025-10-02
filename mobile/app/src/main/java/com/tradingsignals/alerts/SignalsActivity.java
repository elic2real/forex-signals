package com.tradingsignals.alerts;

import android.os.Bundle;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.tradingsignals.alerts.adapters.SignalAdapter;
import com.tradingsignals.alerts.models.TradingSignal;
import com.tradingsignals.alerts.services.ApiService;
import java.util.List;

public class SignalsActivity extends AppCompatActivity {
    private ListView signalsList;
    private ProgressBar progressBar;
    private SignalAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_signals);
        signalsList = findViewById(R.id.signalsList);
        progressBar = findViewById(R.id.progressBar);
        loadSignals();
    }

    private void loadSignals() {
        progressBar.setVisibility(ProgressBar.VISIBLE);
        ApiService.getSignals(this, new ApiService.SignalsCallback() {
            @Override
            public void onSuccess(List<TradingSignal> entries) {
                adapter = new SignalAdapter(SignalsActivity.this, entries);
                signalsList.setAdapter(adapter);
                progressBar.setVisibility(ProgressBar.GONE);
            }
            @Override
            public void onError(String error) {
                Toast.makeText(SignalsActivity.this, "Failed to load signals", Toast.LENGTH_SHORT).show();
                progressBar.setVisibility(ProgressBar.GONE);
            }
        });
    }
}
