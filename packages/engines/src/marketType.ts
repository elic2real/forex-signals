import { EngineSignal, Bias } from '@forex/shared/src/contracts';

export function marketType({ volatility, trendStrength }: { volatility: number; trendStrength: number }): EngineSignal {
  // Score is trendStrength minus normalized volatility
  const score = trendStrength - Math.min(1, volatility / 100);
  const bias: Bias = score > 0.1 ? 'long' : score < -0.1 ? 'short' : 'neutral';
  return {
    id: 'marketType',
    bias,
    score,
    meta: { volatility, trendStrength }
  };
}
