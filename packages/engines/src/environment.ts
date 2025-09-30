import { EngineSignal, Bias } from '@forex/shared/src/contracts';

export function environment({ slope, atr }: { slope: number; atr: number }): EngineSignal {
  // Score is monotonic with slope
  const score = Math.max(-1, Math.min(1, slope / 10));
  const bias: Bias = score > 0.1 ? 'long' : score < -0.1 ? 'short' : 'neutral';
  return {
    id: 'environment',
    bias,
    score,
    meta: { slope, atr }
  };
}
