import axiosInstance from "./axiosInstance";
import type { BrailleCell } from "./brailleAPI";

export type WordAttempt = {
  id: number;
  index: number;
  word: string;
  braille_cells: BrailleCell[];
  user_answer: string;
  is_correct: boolean;
  response_ms: number | null;
  whisper_logprob: number | null;
  created_at: string;
};

export type Session = {
  id: number;
  source_text: string;
  level: 1 | 2 | 3 | 4;
  cell_duration_sec: number;
  total_words: number;
  correct_count: number;
  avg_response_ms: number | null;
  accuracy: number;
  created_at: string;
  finished_at: string | null;
  attempts: WordAttempt[];
};

export async function createSession(params: {
  level: 1 | 2 | 3 | 4;
  cell_duration_sec?: number;
  source_text?: string;
}): Promise<Session> {
  const res = await axiosInstance.post<Session>("/training/sessions/", params);
  return res.data;
}

export async function getSession(id: number): Promise<Session> {
  const res = await axiosInstance.get<Session>(`/training/sessions/${id}/`);
  return res.data;
}

export async function showWord(
  sessionId: number,
  word: string,
  sendHardware = true,
): Promise<{ attempt: WordAttempt; hardware_sent: boolean | null }> {
  const res = await axiosInstance.post(
    `/training/sessions/${sessionId}/show/`,
    { word, send_hardware: sendHardware },
  );
  return res.data;
}

export async function submitAnswer(
  sessionId: number,
  payload: {
    attempt_id: number;
    user_answer: string;
    response_ms?: number;
    whisper_logprob?: number;
  },
): Promise<WordAttempt> {
  const res = await axiosInstance.post<WordAttempt>(
    `/training/sessions/${sessionId}/answer/`,
    payload,
  );
  return res.data;
}

export async function finishSession(sessionId: number): Promise<Session> {
  const res = await axiosInstance.post<Session>(
    `/training/sessions/${sessionId}/finish/`,
  );
  return res.data;
}
