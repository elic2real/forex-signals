import { EngineSignal, Bias } from '@forex/shared/src/contracts';

export function psychology({ fearIndex, greedIndex }: { fearIndex: number; greedIndex: number }): EngineSignal {
  // Score is greed minus fear
  const score = greedIndex - fearIndex;
  const bias: Bias = score > 0.1 ? 'long' : score < -0.1 ? 'short' : 'neutral';
  return {
    id: 'psychology',
    bias,
    score,
    meta: { fearIndex, greedIndex }
  };
}
