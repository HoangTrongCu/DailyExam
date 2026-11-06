import '@testing-library/jest-dom';
import { act, render, screen } from '@testing-library/react';
import { CountdownTimer, formatTime } from '@/components/CountdownTimer';

describe('formatTime', () => {
  it('formats mm:ss', () => {
    expect(formatTime(0)).toBe('00:00');
    expect(formatTime(5)).toBe('00:05');
    expect(formatTime(65)).toBe('01:05');
    expect(formatTime(3600)).toBe('60:00');
  });

  it('clamps negatives', () => {
    expect(formatTime(-10)).toBe('00:00');
  });

  it('floors fractions', () => {
    expect(formatTime(5.9)).toBe('00:05');
  });
});

describe('CountdownTimer', () => {
  beforeEach(() => jest.useFakeTimers());
  afterEach(() => jest.useRealTimers());

  it('renders initial time', () => {
    render(<CountdownTimer totalSeconds={60} />);
    expect(screen.getByRole('timer')).toHaveTextContent('01:00');
  });

  it('counts down', () => {
    render(<CountdownTimer totalSeconds={5} />);
    expect(screen.getByRole('timer')).toHaveTextContent('00:05');
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    expect(screen.getByRole('timer')).toHaveTextContent('00:04');
  });

  it('calls onExpire at zero', () => {
    const onExpire = jest.fn();
    render(<CountdownTimer totalSeconds={1} onExpire={onExpire} />);
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    expect(onExpire).toHaveBeenCalled();
  });

  it('shows warning style when under 60s', () => {
    render(<CountdownTimer totalSeconds={30} />);
    expect(screen.getByRole('timer')).toHaveTextContent('00:30');
  });

  it('does not call onExpire when undefined', () => {
    expect(() => {
      render(<CountdownTimer totalSeconds={1} />);
      act(() => jest.advanceTimersByTime(1000));
    }).not.toThrow();
  });
});
