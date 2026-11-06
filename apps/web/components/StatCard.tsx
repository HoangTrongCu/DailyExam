import React from 'react';

export interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  tone?: 'primary' | 'secondary' | 'accent' | 'success';
  trend?: string;
}

const toneColors: Record<NonNullable<StatCardProps['tone']>, { bg: string; fg: string }> = {
  primary: { bg: 'linear-gradient(135deg, var(--color-blue-500), var(--color-primary))', fg: '#fff' },
  secondary: { bg: 'linear-gradient(135deg, var(--color-yellow-400), var(--color-yellow-500))', fg: '#fff' },
  accent: { bg: 'linear-gradient(135deg, var(--color-pink-400), var(--color-accent))', fg: '#fff' },
  success: { bg: 'linear-gradient(135deg, #4ADE80, var(--color-success))', fg: '#fff' },
};

export function StatCard({ label, value, icon, tone = 'primary', trend }: StatCardProps) {
  const { bg, fg } = toneColors[tone];
  return (
    <div
      role="group"
      aria-label={label}
      style={{
        background: bg,
        color: fg,
        padding: 'var(--spacing-6)',
        borderRadius: 'var(--radius-2xl)',
        boxShadow: 'var(--shadow-clay-md)',
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
        minHeight: 140,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div
          aria-hidden="true"
          style={{
            width: 48,
            height: 48,
            borderRadius: 'var(--radius-xl)',
            background: 'rgba(255, 255, 255, 0.22)',
            display: 'grid',
            placeItems: 'center',
            fontSize: 24,
          }}
        >
          {icon}
        </div>
        {trend ? (
          <span
            style={{
              background: 'rgba(255,255,255,0.22)',
              padding: '4px 10px',
              borderRadius: 'var(--radius-full)',
              fontSize: 12,
              fontWeight: 600,
            }}
          >
            {trend}
          </span>
        ) : null}
      </div>
      <div>
        <div style={{ fontSize: 32, fontFamily: 'var(--font-heading)', fontWeight: 700, lineHeight: 1 }}>{value}</div>
        <div style={{ fontSize: 14, opacity: 0.9, marginTop: 6 }}>{label}</div>
      </div>
    </div>
  );
}
