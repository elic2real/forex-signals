import { EngineSignal, Bias } from '@forex/shared/src/contracts';

export function fundamental({ newsTimeSec, impact }: { newsTimeSec: number; impact: number }): EngineSignal {
  // Veto if high-impact news within 180s
  const veto = impact > 7 && newsTimeSec < 180;
  const score = veto ? 0 : 1 - Math.min(1, newsTimeSec / 600);
  const bias: Bias = veto ? 'neutral' : score > 0.1 ? 'long' : score < -0.1 ? 'short' : 'neutral';
  return {
    id: 'fundamental',
    bias,
    score,
    veto,
    meta: { newsTimeSec, impact }
  };
}
