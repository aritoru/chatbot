import { Intake, InterviewStatus } from '../types';

const BASE = 'http://localhost:8000';

export async function createSession(): Promise<{ session_id: string; message: string }> {
  const res = await fetch(`${BASE}/sessions`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to start session');
  return res.json();
}

export async function sendMessage(
  sessionId: string,
  message: string,
): Promise<{ message: string; status: InterviewStatus; intake: Intake | null; language?: string }> {
  const res = await fetch(`${BASE}/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error('Failed to send message');
  return res.json();
}

export async function closeSession(sessionId: string): Promise<void> {
  await fetch(`${BASE}/sessions/${sessionId}`, { method: 'DELETE' });
}
