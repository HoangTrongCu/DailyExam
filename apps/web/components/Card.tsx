import React from 'react';
import { cn } from '@/lib/utils';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  tone?: 'default' | 'primary' | 'secondary' | 'accent';
  elevated?: boolean;
}

const toneBackground: Record<NonNullable<CardProps['tone']>, string> = {
  default: 'var(--color-surface)',
  primary: 'linear-gradient(135deg, var(--color-blue-100), var(--color-blue-50))',
  secondary: 'linear-gradient(135deg, #FEF3C7, #FFFBEB)',
  accent: 'linear-gradient(135deg, var(--color-pink-100), var(--color-pink-50))',
};

export function Card({
  tone = 'default',
  elevated = false,
  className,
  children,
  ...rest
}: CardProps) {
  const style: React.CSSProperties = {
    background: toneBackground[tone],
    borderRadius: 'var(--radius-2xl)',
    padding: 'var(--spacing-6)',
    boxShadow: elevated ? 'var(--shadow-clay-lg)' : 'var(--shadow-clay-sm)',
    border: '1px solid rgba(255, 255, 255, 0.6)',
  };
  return (
    <div className={cn('clay-card', className)} style={style} {...rest}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className, ...rest }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={cn('clay-card-title', className)}
      style={{ fontSize: '20px', marginBottom: '8px', color: 'var(--color-foreground)' }}
      {...rest}
    >
      {children}
    </h3>
  );
}

export function CardDescription({ children, className, ...rest }: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={cn('clay-card-desc', className)}
      style={{ color: 'var(--color-muted-fg)', fontSize: '15px' }}
      {...rest}
    >
      {children}
    </p>
  );
}
