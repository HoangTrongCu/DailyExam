import '@testing-library/jest-dom';
import { clearAuth, loadAuth, saveAuth } from '@/lib/authStorage';
import type { AuthUser } from '@/lib/api';

const demoUser: AuthUser = {
  user_id: 'u1',
  role: 'student',
  full_name: 'Nam',
  school_id: 'cau_giay',
  access_token: 'tok',
};

describe('authStorage', () => {
  beforeEach(() => window.localStorage.clear());

  it('returns null when empty', () => {
    expect(loadAuth()).toBeNull();
  });

  it('round-trips save/load', () => {
    saveAuth(demoUser);
    expect(loadAuth()).toEqual(demoUser);
  });

  it('clears auth', () => {
    saveAuth(demoUser);
    clearAuth();
    expect(loadAuth()).toBeNull();
  });

  it('handles corrupted value gracefully', () => {
    window.localStorage.setItem('dailyexam.auth', '{not json');
    expect(loadAuth()).toBeNull();
  });
});
