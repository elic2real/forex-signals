import { EngineSignal, Bias } from '@forex/shared/src/contracts';

export function volume({ tickVol, avgVol }: { tickVol: number; avgVol: number }): EngineSignal {
  // Score is normalized tick volume
  const score = avgVol === 0 ? 0 : (tickVol - avgVol) / avgVol;
  const bias: Bias = score > 0.1 ? 'long' : score < -0.1 ? 'short' : 'neutral';
  return {
    id: 'volume',
    bias,
    score,
    meta: { tickVol, avgVol }
  };
}
