'use client';

import React from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { Navbar } from '@/components/Navbar';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Button } from '@/components/Button';
import { useAuth } from '@/components/AuthProvider';
import { api } from '@/lib/api';

type Detail = Awaited<ReturnType<typeof api.mySubmissionDetail>>;

export default function HistoryDetailPage() {
  const router = useRouter();
  const params = useParams();
  const id = Array.isArray(params.id) ? params.id[0] : (params.id ?? '');
  const { user } = useAuth();
  const [detail, setDetail] = React.useState<Detail | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!user) {
      const t = setTimeout(() => router.push('/login'), 200);
      return () => clearTimeout(t);
    }
    api
      .mySubmissionDetail(user.access_token, id)
      .then(setDetail)
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [user, id, router]);

  if (!user) return null;

  return (
    <>
      <Navbar label="Chi tiết bài làm" />
      <main style={{ maxWidth: 900, margin: '0 auto', padding: '40px 24px' }}>
        <Link
          href="/history"
          style={{ color: 'var(--color-primary)', fontWeight: 600, display: 'inline-block', marginBottom: 20 }}
        >
          ← Về lịch sử
        </Link>

        {loading && <Card>Đang tải...</Card>}

        {!loading && error && (
          <Card tone="warm">
            <CardTitle>Không mở được bài làm</CardTitle>
            <p style={{ marginTop: 8 }}>{error}</p>
          </Card>
        )}

        {detail && (
          <>
            <div style={{ marginBottom: 32, textAlign: 'center' }}>
              <CardTitle>Điểm của bạn</CardTitle>
              <p style={{ fontSize: 40, fontFamily: 'var(--font-heading)', fontWeight: 700, marginTop: 8 }}>
                {detail.total_score.toFixed(1)} / {detail.max_total_score.toFixed(1)}{' '}
                <span style={{ color: 'var(--color-primary)' }}>({detail.percentage.toFixed(0)}%)</span>
              </p>
              <div style={{ marginTop: 12 }}>
                {detail.counts_for_ranking ? (
                  <Badge variant="success">Đã tính ranking</Badge>
                ) : (
                  <Badge variant="warning">Làm bù — không tính ranking</Badge>
                )}
              </div>
              <div style={{ marginTop: 8, color: 'var(--color-muted-fg)', fontSize: 14 }}>
                Chấm lúc: {new Date(detail.graded_at).toLocaleString('vi-VN')}
              </div>
            </div>

            <Card>
              <CardTitle>📋 Chi tiết từng câu</CardTitle>
              <CardDescription>Có đáp án chuẩn và lời giải. Nếu thấy chấm chưa đúng, dùng nút "Báo bài chấm sai".</CardDescription>
              <ul style={{ listStyle: 'none', marginTop: 20, display: 'flex', flexDirection: 'column', gap: 12 }}>
                {detail.question_results.map((r) => {
                  const q = detail.exam?.questions.find((x) => x.id === r.question_id);
                  const key = detail.answer_key?.[r.question_id] ?? { correct: '', narrative: '' };
                  return (
                    <li
                      key={r.question_id}
                      style={{
                        padding: 16,
                        background: r.is_correct ? 'var(--green-50)' : '#FEF2F2',
                        borderRadius: 'var(--radius-md)',
                        border: '1px solid rgba(0,0,0,0.04)',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                        <strong>{r.question_id.toUpperCase()}</strong>
                        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                          <Badge variant={r.is_correct ? 'success' : 'danger'}>
                            {r.score.toFixed(2)} / {r.max_score.toFixed(2)} {r.is_correct ? '✓' : '✗'}
                          </Badge>
                          {!r.is_correct && (
                            <AppealButton submissionId={detail.id} questionId={r.question_id} token={user.access_token} />
                          )}
                        </div>
                      </div>
                      {q && (
                        <p style={{ marginTop: 10, fontSize: 15, lineHeight: 1.6 }}>
                          <em>Câu {q.index}:</em> {q.content}
                        </p>
                      )}
                      <div style={{ marginTop: 10, fontSize: 14 }}>
                        <strong style={{ color: 'var(--color-primary)' }}>Đáp án đúng:</strong> {key.correct || '(không có)'}
                      </div>
                      {key.narrative && (
                        <div
                          style={{
                            marginTop: 8,
                            padding: 12,
                            background: '#fff',
                            borderRadius: 'var(--radius-sm)',
                            fontSize: 14,
                            whiteSpace: 'pre-wrap',
                          }}
                        >
                          <strong>Lời giải:</strong>
                          <div style={{ marginTop: 6 }}>{key.narrative}</div>
                        </div>
                      )}
                      {r.feedback && (
                        <div style={{ marginTop: 8, fontSize: 13, color: 'var(--slate-700)' }}>
                          <strong>Nhận xét AI:</strong> {r.feedback}
                        </div>
                      )}
                    </li>
                  );
                })}
              </ul>
            </Card>

            <div style={{ marginTop: 32, textAlign: 'center' }}>
              <Link href="/dashboard">
                <Button variant="primary" size="lg">Về trang chủ</Button>
              </Link>
            </div>
          </>
        )}
      </main>
    </>
  );
}

function AppealButton({ submissionId, questionId, token }: { submissionId: string; questionId: string; token: string }) {
  const [opened, setOpened] = React.useState(false);
  const [reason, setReason] = React.useState('');
  const [done, setDone] = React.useState(false);
  const [loading, setLoading] = React.useState(false);
  const [err, setErr] = React.useState<string | null>(null);

  async function handleAppeal() {
    if (reason.trim().length < 3) {
      setErr('Vui lòng nhập lý do (≥3 ký tự)');
      return;
    }
    setLoading(true);
    setErr(null);
    try {
      await api.appeal(token, submissionId, questionId, reason);
      setDone(true);
    } catch {
      setErr('Không gửi được phúc khảo');
    } finally {
      setLoading(false);
    }
  }

  if (done) return <Badge variant="info">Đã gửi phúc khảo</Badge>;
  if (!opened) {
    return (
      <Button size="sm" variant="ghost" onClick={() => setOpened(true)}>
        Báo bài chấm sai
      </Button>
    );
  }
  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
      <input
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        placeholder="Lý do..."
        aria-label="Lý do phúc khảo"
        style={{
          padding: 8,
          border: `1px solid ${err ? 'var(--red-500)' : 'var(--color-border)'}`,
          borderRadius: 8,
          fontSize: 14,
        }}
      />
      <Button size="sm" variant="accent" onClick={handleAppeal} loading={loading}>
        Gửi
      </Button>
      {err && <span style={{ color: 'var(--red-500)', fontSize: 12 }}>{err}</span>}
    </div>
  );
}
