import clsx, { type ClassValue } from 'clsx';

export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs);
}

export function formatScore(score: number, max: number): string {
  if (max <= 0) return '0 / 0';
  return `${score.toFixed(1)} / ${max.toFixed(1)}`;
}

export function percentage(score: number, max: number): number {
  if (max <= 0) return 0;
  return Math.round((score / max) * 100);
}

export function gradeLetter(percent: number): 'A' | 'B' | 'C' | 'D' | 'F' {
  if (percent >= 90) return 'A';
  if (percent >= 75) return 'B';
  if (percent >= 60) return 'C';
  if (percent >= 40) return 'D';
  return 'F';
}

export function formatDateVi(d: Date): string {
  const day = d.getDate().toString().padStart(2, '0');
  const month = (d.getMonth() + 1).toString().padStart(2, '0');
  return `${day}/${month}/${d.getFullYear()}`;
}

export function formatDuration(seconds: number): string {
  const s = Math.max(0, Math.floor(seconds));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m.toString().padStart(2, '0')}:${r.toString().padStart(2, '0')}`;
}
