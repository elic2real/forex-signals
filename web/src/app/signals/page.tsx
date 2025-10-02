import React from "react";

import React, { useEffect, useState } from "react";

export default function SignalsPage() {
  const [signals, setSignals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/signals")
      .then((res) => res.json())
      .then((data) => {
        setSignals(data.signals || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold mb-4">Live Signals</h1>
      <div className="bg-white rounded shadow p-4">
        {loading ? (
          <p className="text-gray-500">Loading...</p>
        ) : signals.length === 0 ? (
          <p className="text-gray-500">No signals yet.</p>
        ) : (
          <ul>
            {signals.map((signal, i) => (
              <li key={i} className="mb-2 border-b pb-2">
                <div className="font-semibold">{signal.instrument} {signal.direction}</div>
                <div className="text-xs text-gray-400">{new Date(signal.timestamp).toLocaleString()}</div>
                <div className="text-sm">Confidence: {signal.confidence}</div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}
