import { z } from 'zod';

export const Bias = z.enum(['long', 'short', 'neutral']);
export type Bias = z.infer<typeof Bias>;

export const TF = z.enum(['M1','M5','M15','M30','H1','H4','D1']);
export type TF = z.infer<typeof TF>;

export const EngineId = z.enum([
  'environment','correlation','technical','fundamental','marketType','execution','tradeMgmt','volume','conditional','psychology','evaluator'
]);
export type EngineId = z.infer<typeof EngineId>;

export const EngineSignal = z.object({
  id: EngineId,
  bias: Bias,
  score: z.number(),
  veto: z.boolean().optional(),
  keyLevels: z.array(z.number()).optional(),
  ttlMin: z.number().optional(),
  meta: z.record(z.any()).optional()
});
export type EngineSignal = z.infer<typeof EngineSignal>;

export const FusedSignal = z.object({
  bias: Bias,
  score: z.number(),
  keyLevels: z.array(z.number()).optional(),
  orders: z.array(z.object({
    type: z.enum(['market','limit','stop']),
    sl: z.number(),
    tp: z.number(),
    ttlMin: z.number()
  })).optional(),
  veto: z.boolean().optional(),
  meta: z.record(z.any()).optional()
});
export type FusedSignal = z.infer<typeof FusedSignal>;

export const Trade = z.object({
  id: z.string(),
  pair: z.string(),
  tf: TF,
  entry: z.number(),
  sl: z.number(),
  tp: z.number(),
  opened: z.string(),
  closed: z.string().optional(),
  result: z.enum(['win','loss','be','open']),
  meta: z.record(z.any()).optional()
});
export type Trade = z.infer<typeof Trade>;

export const JournalEntry = z.object({
  id: z.string(),
  tradeId: z.string(),
  text: z.string(),
  created: z.string(),
  meta: z.record(z.any()).optional()
});
export type JournalEntry = z.infer<typeof JournalEntry>;

export const Prediction = z.object({
  pair: z.string(),
  tf: TF,
  bias: Bias,
  score: z.number(),
  confidence: z.number(),
  meta: z.record(z.any()).optional()
});
export type Prediction = z.infer<typeof Prediction>;

export const LearnedWeight = z.object({
  pair: z.string(),
  tf: TF,
  regime: z.string(),
  spreadPctl: z.number(),
  minToNews: z.number(),
  weights: z.record(z.number())
});
export type LearnedWeight = z.infer<typeof LearnedWeight>;
