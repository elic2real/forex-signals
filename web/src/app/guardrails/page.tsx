import React from "react";

import React, { useEffect, useState } from "react";

export default function GuardrailsPage() {
  const [status, setStatus] = useState<any>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/guardrails")
      .then((res) => res.json())
      .then((data) => {
        setStatus(data.status || {});
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold mb-4">Guardrails & Risk Controls</h1>
      <div className="bg-white rounded shadow p-4">
        {loading ? (
          <p className="text-gray-500">Loading...</p>
        ) : Object.keys(status).length === 0 ? (
          <p className="text-gray-500">All guardrails nominal.</p>
        ) : (
          <ul>
            {Object.entries(status).map(([name, value]: any, i) => (
              <li key={i} className="mb-2 border-b pb-2">
                <div className="font-semibold">{name}</div>
                <div className="text-sm">{value ? "Active" : "OK"}</div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}
