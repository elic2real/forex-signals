import { EngineSignal, Trade, JournalEntry } from '@forex/shared/src/contracts';

export function buildNarrative(signals: EngineSignal[], trade: Trade, session: string, confluence: number): JournalEntry {
  const text = `Trade ${trade.id} on ${trade.pair} (${trade.tf}):\n` +
    `Bias: ${signals.map(s => s.bias).join(', ')}\n` +
    `SL: ${trade.sl}, TP: ${trade.tp}, Result: ${trade.result}\n` +
    `Session: ${session}, Confluence: ${confluence}`;
  return {
    id: `${trade.id}-journal`,
    tradeId: trade.id,
    text,
    created: new Date().toISOString()
  };
}
