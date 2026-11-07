import React from 'react';
import { cn } from '@/lib/utils';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  tone?: 'default' | 'primary' | 'accent' | 'warm';
  elevated?: boolean;
}

const toneBg: Record<NonNullable<CardProps['tone']>, string> = {
  default: 'var(--color-surface)',
  primary: 'linear-gradient(135deg, var(--amber-100), var(--amber-50))',
  accent: 'linear-gradient(135deg, var(--green-100), var(--green-50))',
  warm: 'linear-gradient(135deg, var(--pink-100), var(--amber-50))',
};

export function Card({ tone = 'default', elevated = false, className, children, ...rest }: CardProps) {
  const style: React.CSSProperties = {
    background: toneBg[tone],
    borderRadius: 'var(--radius-xl)',
    padding: 24,
    boxShadow: elevated ? 'var(--shadow-clay-lg)' : 'var(--shadow-clay-sm)',
    border: '1px solid rgba(255,255,255,0.6)',
  };
  return <div className={cn('clay-card', className)} style={style} {...rest}>{children}</div>;
}

export function CardTitle({ children, className, ...rest }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={cn('clay-card-title', className)}
        style={{ fontSize: 20, marginBottom: 8, color: 'var(--color-foreground)' }}
        {...rest}>
      {children}
    </h3>
  );
}

export function CardDescription({ children, className, ...rest }: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={cn('clay-card-desc', className)}
       style={{ color: 'var(--color-muted-fg)', fontSize: 15 }}
       {...rest}>
      {children}
    </p>
  );
}
