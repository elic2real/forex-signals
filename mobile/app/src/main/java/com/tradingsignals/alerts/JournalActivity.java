package com.tradingsignals.alerts;

import android.os.Bundle;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.tradingsignals.alerts.adapters.JournalAdapter;
import com.tradingsignals.alerts.models.TradingSignal;
import com.tradingsignals.alerts.services.ApiService;
import java.util.List;

public class JournalActivity extends AppCompatActivity {
    private ListView journalList;
    private ProgressBar progressBar;
    private JournalAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_journal);
        journalList = findViewById(R.id.journalList);
        progressBar = findViewById(R.id.progressBar);
        loadJournal();
    }

    private void loadJournal() {
        progressBar.setVisibility(ProgressBar.VISIBLE);
        ApiService.getJournal(this, new ApiService.JournalCallback() {
            @Override
            public void onSuccess(List<TradingSignal> entries) {
                adapter = new JournalAdapter(JournalActivity.this, entries);
                journalList.setAdapter(adapter);
                progressBar.setVisibility(ProgressBar.GONE);
            }
            @Override
            public void onError(String error) {
                Toast.makeText(JournalActivity.this, "Failed to load journal", Toast.LENGTH_SHORT).show();
                progressBar.setVisibility(ProgressBar.GONE);
            }
        });
    }
}
