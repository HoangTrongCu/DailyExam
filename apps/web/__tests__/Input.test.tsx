import '@testing-library/jest-dom';
import { render, screen, fireEvent } from '@testing-library/react';
import { Input } from '@/components/Input';

describe('Input', () => {
  it('renders with label', () => {
    render(<Input label="Email" placeholder="you@mail.vn" />);
    expect(screen.getByText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('you@mail.vn')).toBeInTheDocument();
  });

  it('fires onChange', () => {
    const handle = jest.fn();
    render(<Input label="L" onChange={handle} />);
    fireEvent.change(screen.getByLabelText('L'), { target: { value: 'x' } });
    expect(handle).toHaveBeenCalled();
  });

  it('shows error', () => {
    render(<Input label="L" error="Bad input" />);
    expect(screen.getByText('Bad input')).toBeInTheDocument();
  });

  it('shows helper', () => {
    render(<Input label="L" helper="Hint" />);
    expect(screen.getByText('Hint')).toBeInTheDocument();
  });

  it('works without label', () => {
    const { container } = render(<Input />);
    expect(container.querySelector('input')).toBeInTheDocument();
  });

  it('error takes precedence over helper', () => {
    render(<Input label="L" helper="Hint" error="Bad" />);
    expect(screen.getByText('Bad')).toBeInTheDocument();
    expect(screen.queryByText('Hint')).not.toBeInTheDocument();
  });
});
