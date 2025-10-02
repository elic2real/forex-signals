import React from "react";

import React, { useEffect, useState } from "react";

export default function CalendarPage() {
  const [calendar, setCalendar] = useState<any>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/calendar")
      .then((res) => res.json())
      .then((data) => {
        setCalendar(data.calendar || {});
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold mb-4">Trade Calendar</h1>
      <div className="bg-white rounded shadow p-4">
        {loading ? (
          <p className="text-gray-500">Loading...</p>
        ) : Object.keys(calendar).length === 0 ? (
          <p className="text-gray-500">No calendar data yet.</p>
        ) : (
          <ul>
            {Object.entries(calendar.daily || {}).map(([date, trades]: any, i) => (
              <li key={i} className="mb-2 border-b pb-2">
                <div className="font-semibold">{date}</div>
                <ul className="ml-4">
                  {trades.map((trade: any, j: number) => (
                    <li key={j} className="text-sm">{trade.pair} {trade.side} @ {trade.price}</li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}
