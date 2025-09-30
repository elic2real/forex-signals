import React from 'react';
import { FusedSignal } from '@forex/shared/src/contracts';

export function SignalCard({ signal }: { signal: FusedSignal }) {
  return (
    <div style={{ border: '1px solid #ccc', padding: 12, margin: 8 }}>
      <div>Bias: {signal.bias}</div>
      <div>Score: {signal.score.toFixed(2)}</div>
      {signal.orders && signal.orders.map((o, i) => (
        <div key={i}>
          Order: {o.type}, SL: {o.sl}, TP: {o.tp}, TTL: {o.ttlMin}m
        </div>
      ))}
    </div>
  );
}
