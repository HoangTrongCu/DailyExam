import React from 'react';
import { cn } from '@/lib/utils';

export type ButtonVariant = 'primary' | 'accent' | 'secondary' | 'ghost' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  loading?: boolean;
}

const variantStyle: Record<ButtonVariant, React.CSSProperties> = {
  primary: { background: 'linear-gradient(180deg, var(--amber-400), var(--amber-600))', color: '#fff' },
  accent: { background: 'linear-gradient(180deg, var(--green-500), var(--green-700))', color: '#fff' },
  secondary: { background: 'linear-gradient(180deg, var(--amber-300), var(--amber-500))', color: 'var(--slate-900)' },
  ghost: { background: 'var(--color-surface)', color: 'var(--color-primary)', border: '2px solid var(--amber-200)' },
  danger: { background: 'linear-gradient(180deg, #F87171, var(--red-600))', color: '#fff' },
};

const sizeStyle: Record<ButtonSize, React.CSSProperties> = {
  sm: { padding: '8px 16px', fontSize: 14, borderRadius: 16, minHeight: 40 },
  md: { padding: '12px 24px', fontSize: 16, borderRadius: 20, minHeight: 48 },
  lg: { padding: '16px 32px', fontSize: 18, borderRadius: 24, minHeight: 56 },
};

export function Button({
  variant = 'primary', size = 'md', fullWidth = false, loading = false,
  disabled, className, children, ...rest
}: ButtonProps) {
  const style: React.CSSProperties = {
    ...variantStyle[variant],
    ...sizeStyle[size],
    boxShadow: 'var(--shadow-clay-md)',
    transition: 'var(--button-transition)',
    fontWeight: 700,
    fontFamily: 'var(--font-heading)',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    width: fullWidth ? '100%' : undefined,
    opacity: disabled || loading ? 0.6 : 1,
    cursor: disabled || loading ? 'not-allowed' : 'pointer',
  };
  return (
    <button
      type="button"
      disabled={disabled || loading}
      className={cn('clay-btn', className)}
      style={style}
      aria-busy={loading ? 'true' : 'false'}
      {...rest}
    >
      {loading && <span data-testid="spinner" aria-hidden="true">⟳</span>}
      {children}
    </button>
  );
}
