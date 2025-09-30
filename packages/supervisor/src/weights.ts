type WeightMap = Record<string, number>;

export function resolveWeights(
  pair: string,
  tf: string,
  pairTfWeights: Record<string, WeightMap>,
  pairWeights: Record<string, WeightMap>,
  globalWeights: WeightMap,
  staticWeights: WeightMap
): WeightMap {
  // pair_tf → pair → global → static
  return {
    ...staticWeights,
    ...globalWeights,
    ...pairWeights[pair],
    ...pairTfWeights[`${pair}_${tf}`]
  };
}
