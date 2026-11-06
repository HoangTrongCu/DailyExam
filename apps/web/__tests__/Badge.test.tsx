import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import { Badge } from '@/components/Badge';
import { StatCard } from '@/components/StatCard';

describe('Badge', () => {
  it.each(['default', 'success', 'warning', 'danger', 'info'] as const)('renders %s', (variant) => {
    render(<Badge variant={variant}>Hello</Badge>);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it('defaults to default variant', () => {
    render(<Badge>Default</Badge>);
    expect(screen.getByText('Default')).toBeInTheDocument();
  });
});

describe('StatCard', () => {
  it.each(['primary', 'secondary', 'accent', 'success'] as const)('renders %s tone', (tone) => {
    render(<StatCard label="Test" value={42} icon="📘" tone={tone} />);
    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  it('shows trend when provided', () => {
    render(<StatCard label="L" value={1} icon="🔥" trend="+1" />);
    expect(screen.getByText('+1')).toBeInTheDocument();
  });

  it('uses primary tone by default', () => {
    render(<StatCard label="X" value="Y" icon="🚀" />);
    expect(screen.getByText('Y')).toBeInTheDocument();
  });
});
