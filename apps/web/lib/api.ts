export type Role = 'student' | 'teacher' | 'admin';
export type UserStatus = 'pending' | 'active' | 'rejected';

export interface AuthUser {
  user_id: string;
  role: Role;
  full_name: string;
  school_id: string | null;
  access_token: string;
}

export interface PendingUser {
  id: string;
  email: string;
  full_name: string;
  role: Role;
  status: UserStatus;
  school_id: string | null;
  grade: string | null;
  created_at: string | null;
  approved_at: string | null;
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

export interface RegisterResponse {
  user_id: string;
  status: UserStatus;
  message: string;
}

const DEFAULT_BASE =
  typeof window !== 'undefined'
    ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
    : process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export class ApiError extends Error {
  readonly status: number;
  readonly detail?: string;
  constructor(status: number, message: string, detail?: string) {
    super(message);
    this.status = status;
    this.detail = detail;
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
    let detail: string | undefined;
    try {
      detail = JSON.parse(body).detail;
    } catch {
      // ignore
    }
    throw new ApiError(resp.status, body || resp.statusText, detail);
  }
  if (resp.status === 204) return undefined as T;
  return (await resp.json()) as T;
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  register: (data: { email: string; password: string; full_name: string; role?: Role; school_id?: string | null }) =>
    request<RegisterResponse>('/api/auth/register', { method: 'POST', body: JSON.stringify(data) }),
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
  adminListUsers: (token: string, status: UserStatus = 'pending') =>
    request<PendingUser[]>(`/api/admin/users?status=${status}`, { token }),
  adminApprove: (token: string, userId: string) =>
    request<PendingUser>(`/api/admin/users/${userId}/approve`, { method: 'POST', token }),
  adminReject: (token: string, userId: string) =>
    request<PendingUser>(`/api/admin/users/${userId}/reject`, { method: 'POST', token }),
};
