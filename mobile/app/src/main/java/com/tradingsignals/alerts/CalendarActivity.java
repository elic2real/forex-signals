package com.tradingsignals.alerts;

import android.os.Bundle;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.tradingsignals.alerts.adapters.CalendarAdapter;
import com.tradingsignals.alerts.models.TradingSignal;
import com.tradingsignals.alerts.services.ApiService;
import java.util.List;

public class CalendarActivity extends AppCompatActivity {
    private ListView calendarList;
    private ProgressBar progressBar;
    private CalendarAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_calendar);
        calendarList = findViewById(R.id.calendarList);
        progressBar = findViewById(R.id.progressBar);
        loadCalendar();
    }

    private void loadCalendar() {
        progressBar.setVisibility(ProgressBar.VISIBLE);
        ApiService.getCalendar(this, new ApiService.CalendarCallback() {
            @Override
            public void onSuccess(List<TradingSignal> entries) {
                adapter = new CalendarAdapter(CalendarActivity.this, entries);
                calendarList.setAdapter(adapter);
                progressBar.setVisibility(ProgressBar.GONE);
            }
            @Override
            public void onError(String error) {
                Toast.makeText(CalendarActivity.this, "Failed to load calendar", Toast.LENGTH_SHORT).show();
                progressBar.setVisibility(ProgressBar.GONE);
            }
        });
    }
}
