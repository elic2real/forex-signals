import React from 'react';
import { JournalEntry } from '@forex/shared/src/contracts';

export function JournalCard({ entry }: { entry: JournalEntry }) {
  return (
    <div style={{ border: '1px solid #eee', padding: 10, margin: 8 }}>
      <div>{entry.text}</div>
      <div style={{ fontSize: 12, color: '#888' }}>{entry.created}</div>
    </div>
  );
}
