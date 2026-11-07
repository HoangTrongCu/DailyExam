export type Role = 'student' | 'admin';

export interface AuthUser {
  access_token: string;
  user_id: string;
  role: Role;
  full_name: string;
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

export interface ExamSummary {
  exam_id: string;
  school_id: string;
  school_name: string;
  status: string;
  duration_minutes: number;
  exam_date: string;
  num_questions: number;
}

export interface QuestionResult {
  question_id: string;
  score: number;
  max_score: number;
  is_correct: boolean;
  feedback?: string | null;
  confidence: number;
  chuyen_de?: string;
  type?: string;
}

export interface Submission {
  id: string;
  exam_id: string;
  student_id: string;
  total_score: number;
  max_total_score: number;
  percentage: number;
  question_results: QuestionResult[];
  counts_for_ranking: boolean;
  graded_at: string;
}

export interface AnalyticsEntry {
  chuyen_de: string;
  school_id: string;
  attempts: number;
  correct: number;
  accuracy: number;
  average_score_10: number;
}

export interface RankingEntry {
  rank: number;
  student_id: string;
  full_name: string;
  total: number;
}

export interface RankingResponse {
  period: string;
  school_id: string;
  top: RankingEntry[];
  my_rank: number | null;
}

export class ApiError extends Error {
  readonly status: number;
  readonly detail?: string;
  constructor(status: number, message: string, detail?: string) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

const BASE = typeof window !== 'undefined'
  ? (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001')
  : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001');

async function request<T>(path: string, init: RequestInit & { token?: string | null } = {}): Promise<T> {
  const { token, headers, ...rest } = init;
  const h: Record<string, string> = { 'Content-Type': 'application/json', ...(headers as Record<string, string>) };
  if (token) h.Authorization = `Bearer ${token}`;
  const resp = await fetch(`${BASE}${path}`, { ...rest, headers: h });
  if (!resp.ok) {
    const body = await resp.text();
    let detail: string | undefined;
    try { detail = JSON.parse(body).detail; } catch { /* ignore */ }
    throw new ApiError(resp.status, body || resp.statusText, detail);
  }
  if (resp.status === 204) return undefined as T;
  return (await resp.json()) as T;
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  register: (data: { email: string; password: string; full_name: string; child_name: string }) =>
    request<{ user_id: string; status: string; message: string }>('/api/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  verifyEmail: (token: string) => request<{ success: boolean }>(`/api/auth/verify/${token}`),
  login: (data: { email: string; password: string }) =>
    request<AuthUser>('/api/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  forgotPassword: (email: string) =>
    request<{ message: string }>('/api/auth/forgot-password', { method: 'POST', body: JSON.stringify({ email }) }),
  resetPassword: (token: string, new_password: string) =>
    request<{ success: boolean }>('/api/auth/reset-password', { method: 'POST', body: JSON.stringify({ token, new_password }) }),
  me: (tok: string) => request<{ id: string; email: string; full_name: string; child_name: string; role: Role }>('/api/auth/me', { token: tok }),
  deleteMe: (tok: string) => request<{ success: boolean }>('/api/me', { method: 'DELETE', token: tok }),
  schools: () => request<Array<{ id: string; name: string; short_name: string }>>('/api/schools'),
  examsToday: (tok: string) => request<ExamSummary[]>('/api/exams/today', { token: tok }),
  getExam: (tok: string, id: string) => request<DailyExam>(`/api/exams/${id}`, { token: tok }),
  submit: (tok: string, id: string, answers: Record<string, string>) =>
    request<Submission>(`/api/exams/${id}/submit`, { method: 'POST', body: JSON.stringify({ answers }), token: tok }),
  autosave: (tok: string, id: string, answers: Record<string, string>) =>
    request<{ saved: boolean }>(`/api/exams/${id}/autosave`, { method: 'POST', body: JSON.stringify({ answers }), token: tok }),
  mySubmissions: (tok: string) => request<Submission[]>('/api/me/submissions', { token: tok }),
  mySubmissionDetail: (tok: string, id: string) =>
    request<Submission & { answer_key: Record<string, { correct: string; narrative: string }>; exam: DailyExam | null }>(`/api/me/submissions/${id}`, { token: tok }),
  myAnalytics: (tok: string) => request<AnalyticsEntry[]>('/api/me/analytics', { token: tok }),
  rankings: (tok: string, school_id: string, period = 'total') =>
    request<RankingResponse>(`/api/rankings/${school_id}?period=${period}`, { token: tok }),
  appeal: (tok: string, submission_id: string, question_id: string, reason: string) =>
    request<{ appeal_id: string; status: string }>('/api/appeals', {
      method: 'POST', body: JSON.stringify({ submission_id, question_id, reason }), token: tok,
    }),
  myAppeals: (tok: string) => request<Array<{ id: string; status: string; question_id: string; reason: string; admin_note: string | null }>>('/api/me/appeals', { token: tok }),
  adminStats: (tok: string) => request<{ total_users: number; total_submissions: number; open_appeals: number; exams_today: number }>('/api/admin/stats', { token: tok }),
  adminAppeals: (tok: string) => request<Array<{ id: string; submission_id: string; question_id: string; reason: string; created_at: string }>>('/api/admin/appeals', { token: tok }),
  adminResolveAppeal: (tok: string, id: string, action: 'accept' | 'reject', admin_note?: string, new_correct?: string) =>
    request<{ status: string; affected?: number; changed?: number }>(`/api/admin/appeals/${id}/resolve`, {
      method: 'POST', body: JSON.stringify({ action, admin_note, new_correct }), token: tok,
    }),
  adminUploadBlueprint: (tok: string, school_id: string, structure: object) =>
    request<{ blueprint_id: string; version: number }>('/api/admin/blueprints', {
      method: 'POST', body: JSON.stringify({ school_id, structure }), token: tok,
    }),
};
