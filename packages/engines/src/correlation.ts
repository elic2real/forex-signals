import { EngineSignal, Bias } from '@forex/shared/src/contracts';

export function correlation({ dxy, rls }: { dxy: number; rls: number }): EngineSignal {
  // Bias flips with DXY
  const score = Math.max(-1, Math.min(1, rls / 100));
  const bias: Bias = dxy > 0 ? 'short' : dxy < 0 ? 'long' : 'neutral';
  return {
    id: 'correlation',
    bias,
    score,
    meta: { dxy, rls }
  };
}
