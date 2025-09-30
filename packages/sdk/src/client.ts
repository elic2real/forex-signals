import axios from 'axios';
import { EngineSignal, FusedSignal, Trade, JournalEntry, Prediction } from '@forex/shared/src/contracts';

const api = axios.create({ baseURL: '/api' });

export const getSignals = async (): Promise<FusedSignal[]> => {
  const { data } = await api.get('/v1/signals');
  return data;
};

export const armSignal = async (id: string): Promise<void> => {
  await api.post(`/v1/signals/${id}/arm`);
};

export const getJournal = async (): Promise<JournalEntry[]> => {
  const { data } = await api.get('/v1/journal');
  return data;
};

export const getPerfSummary = async (): Promise<any> => {
  const { data } = await api.get('/v1/perf/summary');
  return data;
};

export const getCalendar = async (): Promise<any> => {
  const { data } = await api.get('/v1/calendar');
  return data;
};
