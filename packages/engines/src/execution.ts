import { EngineSignal, Bias } from '@forex/shared/src/contracts';

export function execution({ spreadPctl, latencyMs }: { spreadPctl: number; latencyMs: number }): EngineSignal {
  // Veto if spread percentile > 90
  const veto = spreadPctl > 90;
  const score = veto ? 0 : 1 - Math.min(1, latencyMs / 500);
  const bias: Bias = veto ? 'neutral' : score > 0.1 ? 'long' : score < -0.1 ? 'short' : 'neutral';
  return {
    id: 'execution',
    bias,
    score,
    veto,
    meta: { spreadPctl, latencyMs }
  };
}
