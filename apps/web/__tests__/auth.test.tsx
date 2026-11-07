import '@testing-library/jest-dom';
import { act, render, screen, fireEvent } from '@testing-library/react';
import { AuthProvider, useAuth } from '@/components/AuthProvider';
import { Navbar } from '@/components/Navbar';
import type { AuthUser } from '@/lib/api';

const push = jest.fn();
jest.mock('next/navigation', () => ({ useRouter: () => ({ push }) }));
jest.mock('next/link', () => ({ __esModule: true, default: ({ children, href }: any) => <a href={href}>{children}</a> }));

const stu: AuthUser = { access_token: 't', user_id: 'u', role: 'student', full_name: 'Minh' };
const adm: AuthUser = { access_token: 't', user_id: 'u', role: 'admin', full_name: 'Admin' };

function Probe({ onReady }: { onReady?: (ctx: ReturnType<typeof useAuth>) => void }) {
  const ctx = useAuth();
  onReady?.(ctx);
  return <div>{ctx.user?.full_name ?? 'anon'}</div>;
}

describe('AuthProvider', () => {
  beforeEach(() => { window.localStorage.clear(); push.mockReset(); });

  it('empty start', () => {
    render(<AuthProvider><Probe /></AuthProvider>);
    expect(screen.getByText('anon')).toBeInTheDocument();
  });

  it('hydrates from storage', () => {
    window.localStorage.setItem('dailyexam.auth', JSON.stringify(stu));
    render(<AuthProvider><Probe /></AuthProvider>);
    expect(screen.getByText('Minh')).toBeInTheDocument();
  });

  it('setUser persists', () => {
    let captured: ReturnType<typeof useAuth> | null = null;
    render(<AuthProvider><Probe onReady={c => (captured = c)} /></AuthProvider>);
    act(() => captured!.setUser(stu));
    expect(JSON.parse(window.localStorage.getItem('dailyexam.auth')!)).toEqual(stu);
  });

  it('setUser(null) clears', () => {
    window.localStorage.setItem('dailyexam.auth', JSON.stringify(stu));
    let captured: ReturnType<typeof useAuth> | null = null;
    render(<AuthProvider><Probe onReady={c => (captured = c)} /></AuthProvider>);
    act(() => captured!.setUser(null));
    expect(window.localStorage.getItem('dailyexam.auth')).toBeNull();
  });

  it('logout clears', () => {
    window.localStorage.setItem('dailyexam.auth', JSON.stringify(stu));
    let captured: ReturnType<typeof useAuth> | null = null;
    render(<AuthProvider><Probe onReady={c => (captured = c)} /></AuthProvider>);
    act(() => captured!.logout());
    expect(window.localStorage.getItem('dailyexam.auth')).toBeNull();
  });
});

describe('Navbar', () => {
  beforeEach(() => { window.localStorage.clear(); push.mockReset(); });

  it('student view', () => {
    window.localStorage.setItem('dailyexam.auth', JSON.stringify(stu));
    render(<AuthProvider><Navbar /></AuthProvider>);
    expect(screen.getByText('Trang chủ')).toBeInTheDocument();
    expect(screen.getByText('Lịch sử')).toBeInTheDocument();
    expect(screen.getByText('Thống kê')).toBeInTheDocument();
  });

  it('admin view', () => {
    window.localStorage.setItem('dailyexam.auth', JSON.stringify(adm));
    render(<AuthProvider><Navbar /></AuthProvider>);
    expect(screen.getByText('Bảng điều khiển')).toBeInTheDocument();
    expect(screen.getByText('Phúc khảo')).toBeInTheDocument();
  });

  it('no user hides links', () => {
    render(<AuthProvider><Navbar /></AuthProvider>);
    expect(screen.queryByLabelText(/Đăng xuất/i)).not.toBeInTheDocument();
  });

  it('logout navigates', () => {
    window.localStorage.setItem('dailyexam.auth', JSON.stringify(stu));
    render(<AuthProvider><Navbar /></AuthProvider>);
    fireEvent.click(screen.getByLabelText('Đăng xuất'));
    expect(push).toHaveBeenCalledWith('/login');
  });

  it('userName override', () => {
    window.localStorage.setItem('dailyexam.auth', JSON.stringify(stu));
    render(<AuthProvider><Navbar userName="Custom" /></AuthProvider>);
    expect(screen.getByLabelText(/User Custom/)).toBeInTheDocument();
  });
});
