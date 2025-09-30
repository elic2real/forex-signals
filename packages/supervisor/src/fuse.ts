import { EngineSignal, FusedSignal } from '@forex/shared/src/contracts';

export function fuse(signals: EngineSignal[], weights: Record<string, number>, newsFreeze: boolean): FusedSignal {
  // Enforce vetoes and news freeze
  const vetoed = signals.some(s => s.veto) || newsFreeze;
  // Weighted sum
  let score = 0;
  let total = 0;
  for (const s of signals) {
    const w = weights[s.id] ?? 1;
    score += s.score * w;
    total += w;
  }
  score = total ? score / total : 0;
  // Bias
  const bias = score > 0.1 ? 'long' : score < -0.1 ? 'short' : 'neutral';
  // Output max 2 conditional orders
  const orders = !vetoed ? [
    { type: 'limit', sl: 10, tp: 20, ttlMin: 60 },
    { type: 'stop', sl: 12, tp: 24, ttlMin: 30 }
  ] : [];
  return {
    bias,
    score,
    orders,
    veto: vetoed
  };
}
