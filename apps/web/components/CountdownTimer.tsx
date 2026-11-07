'use client';

import React from 'react';
import { formatDuration } from '@/lib/utils';

export interface CountdownTimerProps {
  totalSeconds: number;
  onExpire?: () => void;
}

export function CountdownTimer({ totalSeconds, onExpire }: CountdownTimerProps) {
  const [remaining, setRemaining] = React.useState(totalSeconds);

  React.useEffect(() => {
    if (remaining <= 0) {
      onExpire?.();
      return;
    }
    const id = setTimeout(() => setRemaining(r => r - 1), 1000);
    return () => clearTimeout(id);
  }, [remaining, onExpire]);

  const warning = remaining < 60;
  return (
    <div role="timer" aria-live="polite"
         style={{
           display: 'inline-flex', alignItems: 'center', gap: 10,
           padding: '10px 20px',
           background: warning
             ? 'linear-gradient(135deg, #FECACA, var(--red-500))'
             : 'linear-gradient(135deg, var(--amber-400), var(--amber-600))',
           color: '#fff', borderRadius: 'var(--radius-pill)',
           fontFamily: 'var(--font-heading)', fontWeight: 700,
           boxShadow: 'var(--shadow-clay-md)',
         }}>
      <span aria-hidden="true">⏱</span>
      <span>{formatDuration(remaining)}</span>
    </div>
  );
}
