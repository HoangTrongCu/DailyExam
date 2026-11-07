import type { AuthUser } from './api';

const KEY = 'dailyexam.auth';

export function loadAuth(): AuthUser | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = window.localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as AuthUser) : null;
  } catch { return null; }
}

export function saveAuth(u: AuthUser): void {
  if (typeof window !== 'undefined') window.localStorage.setItem(KEY, JSON.stringify(u));
}

export function clearAuth(): void {
  if (typeof window !== 'undefined') window.localStorage.removeItem(KEY);
}
