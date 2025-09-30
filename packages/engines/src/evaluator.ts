import { EngineSignal, Bias } from '@forex/shared/src/contracts';

export function evaluator({ signals }: { signals: EngineSignal[] }): EngineSignal {
  // Score is mean of input scores
  const score = signals.length ? signals.map(s => s.score).reduce((a, b) => a + b, 0) / signals.length : 0;
  const bias: Bias = score > 0.1 ? 'long' : score < -0.1 ? 'short' : 'neutral';
  return {
    id: 'evaluator',
    bias,
    score,
    meta: { signals }
  };
}
