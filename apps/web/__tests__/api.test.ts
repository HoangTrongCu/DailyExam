import '@testing-library/jest-dom';
import { api, ApiError } from '@/lib/api';

function mockResponse(status: number, body: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: 'x',
    json: async () => body,
    text: async () => (typeof body === 'string' ? body : JSON.stringify(body)),
    headers: new Headers(),
  } as unknown as Response;
}

describe('api client', () => {
  const fetchMock = jest.fn();
  beforeEach(() => {
    fetchMock.mockReset();
    (global as any).fetch = fetchMock;
  });

  it('health returns body', async () => {
    fetchMock.mockResolvedValue(mockResponse(200, { status: 'ok' }));
    const r = await api.health();
    expect(r.status).toBe('ok');
  });

  it('login posts credentials', async () => {
    fetchMock.mockResolvedValue(
      mockResponse(200, {
        user_id: 'u1',
        role: 'student',
        full_name: 'A',
        school_id: 'cau_giay',
        access_token: 't',
      }),
    );
    await api.login({ email: 'a@b.c', password: 'pass1234' });
    expect(fetchMock).toHaveBeenCalled();
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toContain('/api/auth/login');
    expect(init.method).toBe('POST');
  });

  it('adds Bearer token', async () => {
    fetchMock.mockResolvedValue(mockResponse(200, []));
    await api.mySubmissions('abc');
    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers.Authorization).toBe('Bearer abc');
  });

  it('throws ApiError on non-2xx', async () => {
    fetchMock.mockResolvedValue(mockResponse(401, 'unauth'));
    await expect(api.me('x')).rejects.toBeInstanceOf(ApiError);
  });

  it('includes status in ApiError', async () => {
    fetchMock.mockResolvedValue(mockResponse(500, 'boom'));
    try {
      await api.schools();
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      expect((e as ApiError).status).toBe(500);
    }
  });

  it('handles 204 no content', async () => {
    fetchMock.mockResolvedValue(mockResponse(204, undefined));
    const r = await api.health();
    expect(r).toBeUndefined();
  });

  it('fetches dailyExam with path', async () => {
    fetchMock.mockResolvedValue(mockResponse(200, { id: 'cau_giay:2026-11-07' }));
    await api.dailyExam('cau_giay', '2026-11-07');
    expect(fetchMock.mock.calls[0][0]).toContain('/api/schools/cau_giay/exams/2026-11-07');
  });

  it('submit sends payload', async () => {
    fetchMock.mockResolvedValue(mockResponse(200, { id: 's1' }));
    await api.submit('t', 'e1', { q1: 'A' });
    const [, init] = fetchMock.mock.calls[0];
    expect(JSON.parse(init.body)).toEqual({ exam_id: 'e1', answers: { q1: 'A' } });
  });

  it('register posts', async () => {
    fetchMock.mockResolvedValue(mockResponse(200, { user_id: 'u' }));
    await api.register({ email: 'a@b.c', password: 'pass1234', full_name: 'A', role: 'student' });
    expect(fetchMock.mock.calls[0][0]).toContain('/api/auth/register');
  });

  it('myAnalytics fetches', async () => {
    fetchMock.mockResolvedValue(mockResponse(200, []));
    await api.myAnalytics('t');
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('adminListUsers passes status in query', async () => {
    fetchMock.mockResolvedValue(mockResponse(200, []));
    await api.adminListUsers('t', 'pending');
    expect(fetchMock.mock.calls[0][0]).toContain('/api/admin/users?status=pending');
  });

  it('adminApprove posts', async () => {
    fetchMock.mockResolvedValue(mockResponse(200, { id: 'u1' }));
    await api.adminApprove('t', 'u1');
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toContain('/api/admin/users/u1/approve');
    expect(init.method).toBe('POST');
  });

  it('adminReject posts', async () => {
    fetchMock.mockResolvedValue(mockResponse(200, { id: 'u1' }));
    await api.adminReject('t', 'u1');
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toContain('/api/admin/users/u1/reject');
    expect(init.method).toBe('POST');
  });

  it('ApiError includes detail', async () => {
    fetchMock.mockResolvedValue(mockResponse(403, { detail: 'Chờ phê duyệt' }));
    try {
      await api.login({ email: 'a@b.c', password: 'x' });
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      expect((e as ApiError).detail).toBe('Chờ phê duyệt');
    }
  });

  it('me adds auth header', async () => {
    fetchMock.mockResolvedValue(mockResponse(200, { id: 'u', email: 'a@b.c', full_name: 'A', role: 'student', school_id: null }));
    await api.me('tok');
    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers.Authorization).toBe('Bearer tok');
  });
});
