import { EngineSignal, Bias } from '@forex/shared/src/contracts';

export function tradeMgmt({ tp1Hit, slToBE, envBias, marketTypeBias }: { tp1Hit: boolean; slToBE: boolean; envBias: Bias; marketTypeBias: Bias }): EngineSignal {
  // Promotion if env+marketType favor trend
  const promotion = envBias === 'long' && marketTypeBias === 'long' ? 'swing' : null;
  const score = tp1Hit ? 1 : slToBE ? 0.5 : 0;
  const bias: Bias = score > 0.1 ? 'long' : score < -0.1 ? 'short' : 'neutral';
  return {
    id: 'tradeMgmt',
    bias,
    score,
    meta: { tp1Hit, slToBE, promotion, envBias, marketTypeBias }
  };
}
