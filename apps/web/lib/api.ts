export type Role = 'student' | 'teacher' | 'admin';

export interface AuthUser {
  user_id: string;
  role: Role;
  full_name: string;
  school_id: string | null;
  access_token: string;
}

export interface Question {
  id: string;
  index: number;
  type: 'multiple_choice' | 'numeric' | 'essay';
  difficulty: 'NB' | 'TH' | 'VD' | 'VDC';
  chuyen_de: string;
  content: string;
  choices: string[] | null;
  max_score: number;
  unit: string | null;
}

export interface DailyExam {
  id: string;
  school_id: string;
  exam_date: string;
  status: string;
  duration_minutes: number;
  questions: Question[];
  gate_open_at: string;
  gate_close_at: string;
}

export interface QuestionResult {
  question_id: string;
  score: number;
  max_score: number;
  is_correct: boolean;
  feedback?: string | null;
  confidence: number;
  chuyen_de?: string;
}

export interface Submission {
  id: string;
  exam_id: string;
  student_id: string;
  total_score: number;
  max_total_score: number;
  percentage: number;
  question_results: QuestionResult[];
  graded_at: string;
}

export interface AnalyticsEntry {
  chuyen_de: string;
  attempts: number;
  correct: number;
  accuracy: number;
  average_score_10: number;
}

const DEFAULT_BASE =
  typeof window !== 'undefined'
    ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
    : process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export class ApiError extends Error {
  readonly status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  init: RequestInit & { token?: string | null } = {},
): Promise<T> {
  const { token, headers, ...rest } = init;
  const finalHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(headers as Record<string, string>),
  };
  if (token) finalHeaders.Authorization = `Bearer ${token}`;
  const base = DEFAULT_BASE;
  const resp = await fetch(`${base}${path}`, { ...rest, headers: finalHeaders });
  if (!resp.ok) {
    const body = await resp.text();
    throw new ApiError(resp.status, body || resp.statusText);
  }
  if (resp.status === 204) return undefined as T;
  return (await resp.json()) as T;
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  register: (data: { email: string; password: string; full_name: string; role: Role; school_id?: string | null }) =>
    request<AuthUser>('/api/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data: { email: string; password: string }) =>
    request<AuthUser>('/api/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  me: (token: string) => request<{ id: string; email: string; full_name: string; role: Role; school_id: string | null }>('/api/auth/me', { token }),
  schools: () => request<Array<{ id: string; name: string }>>('/api/schools'),
  dailyExam: (schoolId: string, date: string) =>
    request<DailyExam>(`/api/schools/${schoolId}/exams/${date}`),
  submit: (token: string, exam_id: string, answers: Record<string, string>) =>
    request<Submission>('/api/submissions', { method: 'POST', body: JSON.stringify({ exam_id, answers }), token }),
  mySubmissions: (token: string) => request<Submission[]>('/api/me/submissions', { token }),
  myAnalytics: (token: string) => request<AnalyticsEntry[]>('/api/me/analytics', { token }),
};
