import React from 'react';
import { cn } from '@/lib/utils';

export type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info';

const variants: Record<BadgeVariant, { bg: string; fg: string }> = {
  default: { bg: 'var(--slate-100)', fg: 'var(--slate-700)' },
  success: { bg: 'var(--green-100)', fg: 'var(--green-700)' },
  warning: { bg: 'var(--amber-100)', fg: 'var(--amber-800)' },
  danger: { bg: '#FEE2E2', fg: '#991B1B' },
  info: { bg: 'var(--amber-50)', fg: 'var(--amber-700)' },
};

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

export function Badge({ variant = 'default', className, children, ...rest }: BadgeProps) {
  const { bg, fg } = variants[variant];
  return (
    <span className={cn('clay-badge', className)}
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            background: bg, color: fg, padding: '4px 12px',
            borderRadius: 'var(--radius-pill)', fontSize: 13, fontWeight: 600,
            fontFamily: 'var(--font-heading)',
          }}
          {...rest}>
      {children}
    </span>
  );
}
