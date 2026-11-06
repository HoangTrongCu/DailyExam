import '@testing-library/jest-dom';
import { act, render, screen } from '@testing-library/react';
import { AuthProvider, useAuth } from '@/components/AuthProvider';
import type { AuthUser } from '@/lib/api';

const sample: AuthUser = {
  user_id: 'u1',
  role: 'student',
  full_name: 'Nam',
  school_id: 'cau_giay',
  access_token: 'tok',
};

function Probe({ onReady }: { onReady?: (ctx: ReturnType<typeof useAuth>) => void }) {
  const ctx = useAuth();
  onReady?.(ctx);
  return <div>{ctx.user?.full_name ?? 'anon'}</div>;
}

describe('AuthProvider', () => {
  beforeEach(() => window.localStorage.clear());

  it('starts with no user', () => {
    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );
    expect(screen.getByText('anon')).toBeInTheDocument();
  });

  it('loads persisted user', () => {
    window.localStorage.setItem('dailyexam.auth', JSON.stringify(sample));
    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );
    expect(screen.getByText('Nam')).toBeInTheDocument();
  });

  it('setUser persists to storage', () => {
    let captured: ReturnType<typeof useAuth> | null = null;
    render(
      <AuthProvider>
        <Probe onReady={(c) => (captured = c)} />
      </AuthProvider>,
    );
    act(() => captured!.setUser(sample));
    expect(JSON.parse(window.localStorage.getItem('dailyexam.auth')!)).toEqual(sample);
  });

  it('logout clears storage', () => {
    window.localStorage.setItem('dailyexam.auth', JSON.stringify(sample));
    let captured: ReturnType<typeof useAuth> | null = null;
    render(
      <AuthProvider>
        <Probe onReady={(c) => (captured = c)} />
      </AuthProvider>,
    );
    act(() => captured!.logout());
    expect(window.localStorage.getItem('dailyexam.auth')).toBeNull();
  });

  it('setUser(null) clears storage', () => {
    window.localStorage.setItem('dailyexam.auth', JSON.stringify(sample));
    let captured: ReturnType<typeof useAuth> | null = null;
    render(
      <AuthProvider>
        <Probe onReady={(c) => (captured = c)} />
      </AuthProvider>,
    );
    act(() => captured!.setUser(null));
    expect(window.localStorage.getItem('dailyexam.auth')).toBeNull();
  });
});
