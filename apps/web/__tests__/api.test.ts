import '@testing-library/jest-dom';
import { api, ApiError } from '@/lib/api';

function resp(status: number, body: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status, statusText: 'x',
    json: async () => body,
    text: async () => (typeof body === 'string' ? body : JSON.stringify(body)),
    headers: new Headers(),
  } as unknown as Response;
}

describe('api client', () => {
  const fetchMock = jest.fn();
  beforeEach(() => { fetchMock.mockReset(); (global as any).fetch = fetchMock; });

  it('health returns body', async () => {
    fetchMock.mockResolvedValue(resp(200, { status: 'ok' }));
    expect((await api.health()).status).toBe('ok');
  });

  it('register posts', async () => {
    fetchMock.mockResolvedValue(resp(200, { user_id: 'u', status: 'pending_verify', message: 'ok' }));
    await api.register({ email: 'a@b.c', password: 'pass1234', full_name: 'A', child_name: 'C' });
    expect(fetchMock.mock.calls[0][0]).toContain('/api/auth/register');
  });

  it('login + token', async () => {
    fetchMock.mockResolvedValue(resp(200, { access_token: 't', user_id: 'u', role: 'student', full_name: 'A' }));
    const user = await api.login({ email: 'a@b.c', password: 'pass1234' });
    expect(user.access_token).toBe('t');
  });

  it('verify email', async () => {
    fetchMock.mockResolvedValue(resp(200, { success: true }));
    await api.verifyEmail('tok');
    expect(fetchMock.mock.calls[0][0]).toContain('/api/auth/verify/tok');
  });

  it('forgot password', async () => {
    fetchMock.mockResolvedValue(resp(200, { message: 'ok' }));
    await api.forgotPassword('a@b.c');
    expect(fetchMock.mock.calls[0][0]).toContain('/api/auth/forgot-password');
  });

  it('reset password', async () => {
    fetchMock.mockResolvedValue(resp(200, { success: true }));
    await api.resetPassword('tok', 'pass1234');
  });

  it('me with token', async () => {
    fetchMock.mockResolvedValue(resp(200, { id: 'u', email: 'a@b.c', full_name: 'A', child_name: 'C', role: 'student' }));
    await api.me('tok');
    expect(fetchMock.mock.calls[0][1].headers.Authorization).toBe('Bearer tok');
  });

  it('delete me', async () => {
    fetchMock.mockResolvedValue(resp(200, { success: true }));
    await api.deleteMe('tok');
    expect(fetchMock.mock.calls[0][1].method).toBe('DELETE');
  });

  it('exams today', async () => {
    fetchMock.mockResolvedValue(resp(200, []));
    await api.examsToday('t');
    expect(fetchMock.mock.calls[0][0]).toContain('/api/exams/today');
  });

  it('get exam', async () => {
    fetchMock.mockResolvedValue(resp(200, { id: 'e1' }));
    await api.getExam('t', 'e1');
  });

  it('submit posts answers', async () => {
    fetchMock.mockResolvedValue(resp(200, { id: 's1' }));
    await api.submit('t', 'e1', { q1: 'A' });
    const [, init] = fetchMock.mock.calls[0];
    expect(JSON.parse(init.body)).toEqual({ answers: { q1: 'A' } });
  });

  it('autosave', async () => {
    fetchMock.mockResolvedValue(resp(200, { saved: true }));
    await api.autosave('t', 'e1', { q1: 'A' });
  });

  it('my submissions / detail / analytics / rankings', async () => {
    fetchMock.mockResolvedValue(resp(200, []));
    await api.mySubmissions('t'); await api.mySubmissionDetail('t', 's1');
    await api.myAnalytics('t'); await api.rankings('t', 'cau_giay');
    expect(fetchMock).toHaveBeenCalledTimes(4);
  });

  it('appeal', async () => {
    fetchMock.mockResolvedValue(resp(200, { appeal_id: 'a1', status: 'open' }));
    await api.appeal('t', 's1', 'q1', 'reason');
  });

  it('my appeals', async () => {
    fetchMock.mockResolvedValue(resp(200, []));
    await api.myAppeals('t');
  });

  it('admin stats / appeals / resolve / blueprint', async () => {
    fetchMock.mockResolvedValue(resp(200, {}));
    await api.adminStats('t');
    await api.adminAppeals('t');
    await api.adminResolveAppeal('t', 'a1', 'accept', 'ok', '27');
    await api.adminUploadBlueprint('t', 'cau_giay', { x: 1 });
    expect(fetchMock).toHaveBeenCalledTimes(4);
  });

  it('schools', async () => {
    fetchMock.mockResolvedValue(resp(200, []));
    await api.schools();
  });

  it('204 returns undefined', async () => {
    fetchMock.mockResolvedValue(resp(204, undefined));
    const r = await api.deleteMe('t');
    expect(r).toBeUndefined();
  });

  it('throws ApiError with detail', async () => {
    fetchMock.mockResolvedValue(resp(403, { detail: 'denied' }));
    try { await api.me('t'); } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      expect((e as ApiError).status).toBe(403);
      expect((e as ApiError).detail).toBe('denied');
    }
  });

  it('throws ApiError on plain text', async () => {
    fetchMock.mockResolvedValue(resp(500, 'boom'));
    await expect(api.schools()).rejects.toBeInstanceOf(ApiError);
  });
});
