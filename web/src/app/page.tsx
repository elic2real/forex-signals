import { useEffect, useState, useRef } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function Home() {
  const [eurusdPrices, setEurusdPrices] = useState<number[]>([]);
  const [labels, setLabels] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    let ws: WebSocket | null = null;
    let wsConnected = false;

    const handlePrice = (price: number) => {
      setEurusdPrices((prev) => [...prev.slice(-19), price]);
      setLabels((prev) => [
        ...prev.slice(-19),
        new Date().toLocaleTimeString(),
      ]);
      setLoading(false);
    };

    // Try WebSocket first
    try {
      ws = new WebSocket("ws://localhost:8002/ws/eurusd");
      wsRef.current = ws;
      ws.onopen = () => {
        wsConnected = true;
      };
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const price = data.price || data.current_price || data;
          if (typeof price === "number") {
            handlePrice(price);
          }
        } catch (e) {
          // ignore
        }
      };
      ws.onerror = () => {
        setError("WebSocket error, falling back to HTTP polling");
      };
      ws.onclose = () => {
        if (!wsConnected) {
          // fallback to HTTP polling if WebSocket fails to connect
          pollHttp();
        }
      };
    } catch (e) {
      pollHttp();
    }

    function pollHttp() {
      const fetchData = async () => {
        try {
          const res = await fetch("http://localhost:8002/active-signals");
          const data = await res.json();
          const price = data.market_data?.EUR_USD?.current_price;
          if (price) {
            handlePrice(price);
          }
        } catch (err) {
          setError("Could not fetch price data");
        }
      };
      fetchData();
      interval = setInterval(fetchData, 5000);
    }

    return () => {
      if (wsRef.current) wsRef.current.close();
      if (interval) clearInterval(interval);
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold text-blue-400 mb-6">💹 Forex Signals Dashboard</h1>
      <div className="bg-gray-800 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">EUR/USD Price (Live)</h2>
        {loading ? (
          <div>Loading chart...</div>
        ) : error ? (
          <div className="text-red-400">{error}</div>
        ) : (
          <Line
            data={{
              labels,
              datasets: [
                {
                  label: "EUR/USD",
                  data: eurusdPrices,
                  borderColor: "#3b82f6",
                  backgroundColor: "rgba(59,130,246,0.2)",
                  tension: 0.3,
                },
              ],
            }}
            options={{
              responsive: true,
              plugins: {
                legend: { display: false },
                title: {
                  display: false,
                },
              },
              scales: {
                x: {
                  ticks: { color: "#d1d5db" },
                  grid: { color: "#374151" },
                },
                y: {
                  ticks: { color: "#d1d5db" },
                  grid: { color: "#374151" },
                },
              },
            }}
          />
        )}
      </div>
    </div>
  );
}
