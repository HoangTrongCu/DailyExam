import '@testing-library/jest-dom';
import { clearAuth, loadAuth, saveAuth } from '@/lib/authStorage';

const user = { access_token: 't', user_id: 'u1', role: 'student' as const, full_name: 'Nam' };

describe('authStorage', () => {
  beforeEach(() => window.localStorage.clear());

  it('null when empty', () => expect(loadAuth()).toBeNull());
  it('round-trip', () => { saveAuth(user); expect(loadAuth()).toEqual(user); });
  it('clear', () => { saveAuth(user); clearAuth(); expect(loadAuth()).toBeNull(); });
  it('corrupted value', () => {
    window.localStorage.setItem('dailyexam.auth', '{not json');
    expect(loadAuth()).toBeNull();
  });
});
