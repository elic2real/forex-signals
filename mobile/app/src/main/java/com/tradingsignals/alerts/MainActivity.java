package com.tradingsignals.alerts;

import android.content.Intent;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.tradingsignals.alerts.adapters.SignalAdapter;
import com.tradingsignals.alerts.models.TradingSignal;
import com.tradingsignals.alerts.services.ApiService;

import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    
    private RecyclerView recyclerView;
    private SignalAdapter signalAdapter;
    private SwipeRefreshLayout swipeRefreshLayout;
    private ApiService apiService;
    private List<TradingSignal> signalList;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        initializeViews();
        setupRecyclerView();
        setupSwipeRefresh();
        initializeApiService();
        loadSignals();
    }
    
    private void initializeViews() {
        recyclerView = findViewById(R.id.recyclerViewSignals);
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout);
        signalList = new ArrayList<>();
    }
    
    private void setupRecyclerView() {
        signalAdapter = new SignalAdapter(signalList, this::onSignalClick);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        recyclerView.setAdapter(signalAdapter);
    }
    
    private void setupSwipeRefresh() {
        swipeRefreshLayout.setOnRefreshListener(this::loadSignals);
        swipeRefreshLayout.setColorSchemeResources(
            R.color.colorPrimary,
            R.color.colorAccent
        );
    }
    
    private void initializeApiService() {
        apiService = new ApiService(this);
    }
    
    private void loadSignals() {
        swipeRefreshLayout.setRefreshing(true);
        
        apiService.getSignals(new ApiService.ApiCallback<List<TradingSignal>>() {
            @Override
            public void onSuccess(List<TradingSignal> result) {
                runOnUiThread(() -> {
                    swipeRefreshLayout.setRefreshing(false);
                    signalList.clear();
                    signalList.addAll(result);
                    signalAdapter.notifyDataSetChanged();
                });
            }
            
            @Override
            public void onError(String error) {
                runOnUiThread(() -> {
                    swipeRefreshLayout.setRefreshing(false);
                    showError("Error loading signals: " + error);
                });
            }
        });
    }
    
    private void onSignalClick(TradingSignal signal) {
        Intent intent = new Intent(this, SignalDetailsActivity.class);
        intent.putExtra("signal", signal);
        startActivity(intent);
    }
    
    private void showError(String message) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    }
    
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main_menu, menu);
        return true;
    }
    
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();
        
        if (id == R.id.action_refresh) {
            loadSignals();
            return true;
        } else if (id == R.id.action_settings) {
            Intent intent = new Intent(this, SettingsActivity.class);
            startActivity(intent);
            return true;
        }
        
        return super.onOptionsItemSelected(item);
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        // Refresh signals when returning to the activity
        loadSignals();
    }
}
