import { EngineSignal, Bias } from '@forex/shared/src/contracts';

export function conditional({ expiryMin, isExpired }: { expiryMin: number; isExpired: boolean }): EngineSignal {
  // TTL expiry marks expired
  const score = isExpired ? 0 : 1 - Math.min(1, expiryMin / 60);
  const bias: Bias = isExpired ? 'neutral' : score > 0.1 ? 'long' : score < -0.1 ? 'short' : 'neutral';
  return {
    id: 'conditional',
    bias,
    score,
    ttlMin: expiryMin,
    meta: { expiryMin, isExpired }
  };
}
