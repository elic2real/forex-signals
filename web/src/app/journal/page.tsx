import React from "react";

import React, { useEffect, useState } from "react";

export default function JournalPage() {
  const [entries, setEntries] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/journal")
      .then((res) => res.json())
      .then((data) => {
        setEntries(data.entries || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold mb-4">Trade Journal</h1>
      <div className="bg-white rounded shadow p-4">
        {loading ? (
          <p className="text-gray-500">Loading...</p>
        ) : entries.length === 0 ? (
          <p className="text-gray-500">No journal entries yet.</p>
        ) : (
          <ul>
            {entries.map((entry, i) => (
              <li key={i} className="mb-2 border-b pb-2">
                <div className="font-semibold">{entry.pair} {entry.side}</div>
                <div className="text-xs text-gray-400">{new Date(entry.timestamp * 1000).toLocaleString()}</div>
                <div className="text-sm">{entry.narrative}</div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}
