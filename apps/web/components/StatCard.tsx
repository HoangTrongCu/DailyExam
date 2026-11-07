import React from 'react';

export interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  tone?: 'primary' | 'accent' | 'warm' | 'secondary';
}

const tones: Record<NonNullable<StatCardProps['tone']>, { bg: string; fg: string }> = {
  primary: { bg: 'linear-gradient(135deg, var(--amber-400), var(--amber-600))', fg: '#fff' },
  accent: { bg: 'linear-gradient(135deg, var(--green-500), var(--green-700))', fg: '#fff' },
  warm: { bg: 'linear-gradient(135deg, var(--pink-400), var(--pink-500))', fg: '#fff' },
  secondary: { bg: 'linear-gradient(135deg, var(--amber-300), var(--amber-500))', fg: 'var(--slate-900)' },
};

export function StatCard({ label, value, icon, tone = 'primary' }: StatCardProps) {
  const { bg, fg } = tones[tone];
  return (
    <div role="group" aria-label={label}
         style={{
           background: bg, color: fg, padding: 24,
           borderRadius: 'var(--radius-xl)',
           boxShadow: 'var(--shadow-clay-md)',
           display: 'flex', flexDirection: 'column', gap: 12, minHeight: 140,
         }}>
      <div aria-hidden="true" style={{
        width: 48, height: 48, borderRadius: 'var(--radius-md)',
        background: 'rgba(255,255,255,0.22)', display: 'grid', placeItems: 'center', fontSize: 24,
      }}>{icon}</div>
      <div>
        <div style={{ fontSize: 32, fontFamily: 'var(--font-heading)', fontWeight: 700, lineHeight: 1 }}>{value}</div>
        <div style={{ fontSize: 14, opacity: 0.9, marginTop: 6 }}>{label}</div>
      </div>
    </div>
  );
}
