import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  helper?: string;
  error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, helper, error, id, style, ...rest }, ref,
) {
  const autoId = React.useId();
  const inputId = id ?? autoId;
  return (
    <label htmlFor={inputId} style={{ display: 'block', marginBottom: 16 }}>
      {label && (
        <div style={{ fontFamily: 'var(--font-heading)', fontWeight: 600, fontSize: 14, marginBottom: 6, color: 'var(--slate-700)' }}>
          {label}
        </div>
      )}
      <input
        ref={ref} id={inputId}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={helper || error ? `${inputId}-helper` : undefined}
        style={{
          width: '100%', padding: 14, fontSize: 16, fontFamily: 'var(--font-body)',
          border: `2px solid ${error ? 'var(--red-500)' : 'var(--color-border)'}`,
          borderRadius: 'var(--radius-md)',
          boxShadow: 'var(--shadow-clay-inset)',
          background: '#fff',
          ...style,
        }}
        {...rest}
      />
      {(helper || error) && (
        <div id={`${inputId}-helper`} style={{
          fontSize: 13, marginTop: 6,
          color: error ? 'var(--red-500)' : 'var(--color-muted-fg)',
        }}>
          {error ?? helper}
        </div>
      )}
    </label>
  );
});
