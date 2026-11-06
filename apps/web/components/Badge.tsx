import React from 'react';
import { cn } from '@/lib/utils';

export type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info';

const variants: Record<BadgeVariant, { bg: string; fg: string }> = {
  default: { bg: 'var(--color-slate-100)', fg: 'var(--color-slate-700)' },
  success: { bg: '#DCFCE7', fg: '#166534' },
  warning: { bg: '#FEF3C7', fg: '#92400E' },
  danger: { bg: '#FEE2E2', fg: '#991B1B' },
  info: { bg: 'var(--color-blue-100)', fg: 'var(--color-blue-800)' },
};

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

export function Badge({ variant = 'default', className, children, ...rest }: BadgeProps) {
  const { bg, fg } = variants[variant];
  return (
    <span
      className={cn('clay-badge', className)}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        background: bg,
        color: fg,
        padding: '4px 12px',
        borderRadius: 'var(--radius-full)',
        fontSize: '13px',
        fontWeight: 600,
        fontFamily: 'var(--font-heading)',
      }}
      {...rest}
    >
      {children}
    </span>
  );
}
