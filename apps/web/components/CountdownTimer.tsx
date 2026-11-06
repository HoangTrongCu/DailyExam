'use client';

import React from 'react';

export interface CountdownTimerProps {
  totalSeconds: number;
  onExpire?: () => void;
}

export function formatTime(seconds: number): string {
  const safe = Math.max(0, Math.floor(seconds));
  const m = Math.floor(safe / 60);
  const s = safe % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

export function CountdownTimer({ totalSeconds, onExpire }: CountdownTimerProps) {
  const [remaining, setRemaining] = React.useState(totalSeconds);

  React.useEffect(() => {
    if (remaining <= 0) {
      onExpire?.();
      return;
    }
    const id = setTimeout(() => setRemaining((r) => r - 1), 1000);
    return () => clearTimeout(id);
  }, [remaining, onExpire]);

  const warning = remaining < 60;
  return (
    <div
      role="timer"
      aria-live="polite"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 10,
        padding: '10px 20px',
        background: warning ? 'linear-gradient(135deg, #FECACA, var(--color-red-500))' : 'linear-gradient(135deg, var(--color-blue-200), var(--color-primary))',
        color: '#fff',
        borderRadius: 'var(--radius-full)',
        fontFamily: 'var(--font-heading)',
        fontWeight: 700,
        boxShadow: 'var(--shadow-clay-md)',
      }}
    >
      <span aria-hidden="true">⏱</span>
      <span>{formatTime(remaining)}</span>
    </div>
  );
}
