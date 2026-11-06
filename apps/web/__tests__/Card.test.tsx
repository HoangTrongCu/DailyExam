import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import { Card, CardTitle, CardDescription } from '@/components/Card';

describe('Card', () => {
  it('renders children', () => {
    render(<Card>Hello</Card>);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it.each(['default', 'primary', 'secondary', 'accent'] as const)('renders %s tone', (tone) => {
    render(<Card tone={tone}>Content</Card>);
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('renders elevated', () => {
    render(<Card elevated>Hi</Card>);
    expect(screen.getByText('Hi')).toBeInTheDocument();
  });
});

describe('CardTitle', () => {
  it('renders as heading', () => {
    render(<CardTitle>Title</CardTitle>);
    expect(screen.getByRole('heading', { name: /title/i })).toBeInTheDocument();
  });
});

describe('CardDescription', () => {
  it('renders description', () => {
    render(<CardDescription>Desc</CardDescription>);
    expect(screen.getByText('Desc')).toBeInTheDocument();
  });
});
