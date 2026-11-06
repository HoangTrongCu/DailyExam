import React from 'react';
import { cn } from '@/lib/utils';

export type ButtonVariant = 'primary' | 'secondary' | 'accent' | 'ghost';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  loading?: boolean;
}

const variantStyles: Record<ButtonVariant, React.CSSProperties> = {
  primary: {
    background: 'linear-gradient(180deg, var(--color-blue-500), var(--color-primary))',
    color: '#fff',
  },
  secondary: {
    background: 'linear-gradient(180deg, var(--color-yellow-400), var(--color-secondary))',
    color: '#fff',
  },
  accent: {
    background: 'linear-gradient(180deg, var(--color-pink-400), var(--color-accent))',
    color: '#fff',
  },
  ghost: {
    background: 'var(--color-surface)',
    color: 'var(--color-primary)',
    border: '2px solid var(--color-blue-200)',
  },
};

const sizeStyles: Record<ButtonSize, React.CSSProperties> = {
  sm: { padding: '8px 16px', fontSize: '14px', borderRadius: '16px', minHeight: '40px' },
  md: { padding: '12px 24px', fontSize: '16px', borderRadius: '20px', minHeight: '48px' },
  lg: { padding: '16px 32px', fontSize: '18px', borderRadius: '24px', minHeight: '56px' },
};

export function Button({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  disabled,
  className,
  children,
  ...rest
}: ButtonProps) {
  const style: React.CSSProperties = {
    ...variantStyles[variant],
    ...sizeStyles[size],
    boxShadow: 'var(--shadow-clay-md)',
    transition: 'var(--button-transition)',
    fontWeight: 700,
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    width: fullWidth ? '100%' : undefined,
    opacity: disabled || loading ? 0.6 : 1,
    cursor: disabled || loading ? 'not-allowed' : 'pointer',
    fontFamily: 'var(--font-heading)',
  };

  return (
    <button
      type="button"
      disabled={disabled || loading}
      className={cn('clay-button', className)}
      style={style}
      aria-busy={loading ? 'true' : 'false'}
      {...rest}
    >
      {loading && <span data-testid="button-spinner">⏳</span>}
      {children}
    </button>
  );
}
