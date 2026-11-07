import '@testing-library/jest-dom';
import { act, render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/Button';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Input } from '@/components/Input';
import { StatCard } from '@/components/StatCard';
import { CountdownTimer } from '@/components/CountdownTimer';

describe('Button', () => {
  it('renders', () => {
    render(<Button>Click</Button>);
    expect(screen.getByRole('button', { name: /click/i })).toBeInTheDocument();
  });

  it('onClick fires', () => {
    const f = jest.fn();
    render(<Button onClick={f}>G</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(f).toHaveBeenCalled();
  });

  it('loading disables + spinner', () => {
    render(<Button loading>X</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
    expect(screen.getByTestId('spinner')).toBeInTheDocument();
  });

  it('disabled', () => {
    render(<Button disabled>X</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it.each(['primary', 'accent', 'secondary', 'ghost', 'danger'] as const)('variant %s', (v) => {
    render(<Button variant={v}>V</Button>);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it.each(['sm', 'md', 'lg'] as const)('size %s', (s) => {
    render(<Button size={s}>S</Button>);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('fullWidth style', () => {
    const { container } = render(<Button fullWidth>W</Button>);
    expect(container.querySelector('button')!.style.width).toBe('100%');
  });
});

describe('Card', () => {
  it.each(['default', 'primary', 'accent', 'warm'] as const)('tone %s', (tone) => {
    render(<Card tone={tone}>Hi</Card>);
    expect(screen.getByText('Hi')).toBeInTheDocument();
  });

  it('elevated', () => { render(<Card elevated>E</Card>); expect(screen.getByText('E')).toBeInTheDocument(); });

  it('title + description', () => {
    render(<><CardTitle>T</CardTitle><CardDescription>D</CardDescription></>);
    expect(screen.getByRole('heading', { name: 'T' })).toBeInTheDocument();
    expect(screen.getByText('D')).toBeInTheDocument();
  });
});

describe('Badge', () => {
  it.each(['default', 'success', 'warning', 'danger', 'info'] as const)('variant %s', (v) => {
    render(<Badge variant={v}>B</Badge>);
    expect(screen.getByText('B')).toBeInTheDocument();
  });
  it('default variant', () => { render(<Badge>X</Badge>); expect(screen.getByText('X')).toBeInTheDocument(); });
});

describe('Input', () => {
  it('label + input', () => {
    render(<Input label="Email" placeholder="you@x" />);
    expect(screen.getByText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('you@x')).toBeInTheDocument();
  });
  it('onChange', () => {
    const f = jest.fn();
    render(<Input label="L" onChange={f} />);
    fireEvent.change(screen.getByLabelText('L'), { target: { value: 'x' } });
    expect(f).toHaveBeenCalled();
  });
  it('error shown', () => {
    render(<Input label="L" error="bad" />);
    expect(screen.getByText('bad')).toBeInTheDocument();
  });
  it('helper shown', () => {
    render(<Input label="L" helper="hint" />);
    expect(screen.getByText('hint')).toBeInTheDocument();
  });
  it('error overrides helper', () => {
    render(<Input label="L" helper="h" error="e" />);
    expect(screen.getByText('e')).toBeInTheDocument();
    expect(screen.queryByText('h')).not.toBeInTheDocument();
  });
  it('no label', () => {
    const { container } = render(<Input />);
    expect(container.querySelector('input')).toBeInTheDocument();
  });
});

describe('StatCard', () => {
  it.each(['primary', 'accent', 'warm', 'secondary'] as const)('tone %s', (t) => {
    render(<StatCard label="L" value={42} icon="X" tone={t} />);
    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByText('L')).toBeInTheDocument();
  });
  it('default tone', () => {
    render(<StatCard label="L" value="V" icon="X" />);
    expect(screen.getByText('V')).toBeInTheDocument();
  });
});

describe('CountdownTimer', () => {
  beforeEach(() => jest.useFakeTimers());
  afterEach(() => jest.useRealTimers());

  it('renders', () => {
    render(<CountdownTimer totalSeconds={60} />);
    expect(screen.getByRole('timer')).toHaveTextContent('01:00');
  });

  it('counts down', () => {
    render(<CountdownTimer totalSeconds={5} />);
    act(() => { jest.advanceTimersByTime(1000); });
    expect(screen.getByRole('timer')).toHaveTextContent('00:04');
  });

  it('onExpire fires at 0', () => {
    const f = jest.fn();
    render(<CountdownTimer totalSeconds={1} onExpire={f} />);
    act(() => { jest.advanceTimersByTime(1000); });
    expect(f).toHaveBeenCalled();
  });

  it('warning style under 60s', () => {
    render(<CountdownTimer totalSeconds={30} />);
    expect(screen.getByRole('timer')).toHaveTextContent('00:30');
  });

  it('no callback when undefined', () => {
    expect(() => {
      render(<CountdownTimer totalSeconds={1} />);
      act(() => jest.advanceTimersByTime(1000));
    }).not.toThrow();
  });
});
