import { EngineSignal, Bias } from '@forex/shared/src/contracts';

export function technical({ rsi, macd, maSlope }: { rsi: number; macd: number; maSlope: number }): EngineSignal {
  // Score is a weighted sum of normalized indicators
  const score = (rsi - 50) / 50 * 0.4 + macd * 0.4 + maSlope * 0.2;
  const bias: Bias = score > 0.1 ? 'long' : score < -0.1 ? 'short' : 'neutral';
  return {
    id: 'technical',
    bias,
    score,
    meta: { rsi, macd, maSlope }
  };
}
