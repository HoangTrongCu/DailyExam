'use client';

import React from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { Navbar } from '@/components/Navbar';
import { Card, CardTitle } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Button } from '@/components/Button';
import { CountdownTimer } from '@/components/CountdownTimer';
import { useAuth } from '@/components/AuthProvider';
import { api, type DailyExam, type Submission } from '@/lib/api';

export default function ExamPage() {
  const router = useRouter();
  const params = useParams();
  const id = Array.isArray(params.id) ? params.id[0] : (params.id ?? '');
  const { user } = useAuth();
  const [exam, setExam] = React.useState<DailyExam | null>(null);
  const [answers, setAnswers] = React.useState<Record<string, string>>({});
  const [loading, setLoading] = React.useState(true);
  const [submitting, setSubmitting] = React.useState(false);
  const [result, setResult] = React.useState<Submission | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!user) { const t = setTimeout(() => router.push('/login'), 200); return () => clearTimeout(t); }
    api.getExam(user.access_token, id)
      .then(setExam)
      .catch(e => setError(String(e)))
      .finally(() => setLoading(false));
  }, [user, id, router]);

  // Anti-download: disable right-click, copy, print
  React.useEffect(() => {
    const prevent = (e: Event) => e.preventDefault();
    window.addEventListener('contextmenu', prevent);
    window.addEventListener('copy', prevent);
    return () => {
      window.removeEventListener('contextmenu', prevent);
      window.removeEventListener('copy', prevent);
    };
  }, []);

  async function handleSubmit() {
    if (!user || !exam) return;
    setSubmitting(true);
    try {
      const sub = await api.submit(user.access_token, exam.id, answers);
      setResult(sub);
    } catch (e) { setError(String(e)); }
    finally { setSubmitting(false); }
  }

  if (!user) return null;
  if (result) return <ResultView result={result} examId={id} />;

  return (
    <>
      <Navbar label={`Đang làm bài · ${exam?.school_id ?? ''}`} />
      <main style={{ maxWidth: 900, margin: '0 auto', padding: '32px 24px' }}
            onCopy={e => e.preventDefault()}>
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          marginBottom: 32, flexWrap: 'wrap', gap: 16,
        }}>
          <div>
            <Badge variant="info">Đề ngày {new Date().toLocaleDateString('vi-VN')}</Badge>
            <h1 style={{ marginTop: 10, fontSize: 32 }}>Đề thi Toán hôm nay</h1>
          </div>
          {exam && <CountdownTimer totalSeconds={(exam.duration_minutes ?? 60) * 60} onExpire={handleSubmit} />}
        </div>

        {loading && <Card>Đang tải đề...</Card>}
        {error && !exam && (
          <Card tone="warm">
            <CardTitle>Không mở được đề</CardTitle>
            <p style={{ marginTop: 8 }}>{error}</p>
            <div style={{ marginTop: 16 }}>
              <Link href="/dashboard"><Button variant="ghost">Về Dashboard</Button></Link>
            </div>
          </Card>
        )}

        {exam && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            {exam.questions.map((q) => (
              <Card key={q.id} tone={q.type === 'essay' ? 'accent' : 'default'}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12, flexWrap: 'wrap' }}>
                  <div aria-hidden="true" style={{
                    width: 36, height: 36, borderRadius: 'var(--radius-pill)',
                    background: 'linear-gradient(135deg, var(--amber-400), var(--amber-600))',
                    color: '#fff', display: 'grid', placeItems: 'center',
                    fontWeight: 700, fontFamily: 'var(--font-heading)',
                  }}>{q.index}</div>
                  <Badge variant={q.type === 'multiple_choice' ? 'info' : q.type === 'numeric' ? 'warning' : 'success'}>
                    {q.type === 'multiple_choice' ? 'Trắc nghiệm' : q.type === 'numeric' ? 'Điền số' : 'Tự luận'}
                  </Badge>
                  <Badge variant="default">{q.max_score.toFixed(2)} điểm</Badge>
                  <Badge variant="default">{q.difficulty}</Badge>
                </div>
                <CardTitle>Câu {q.index}</CardTitle>
                <p style={{ fontSize: 17, lineHeight: 1.6, marginBottom: 18 }}>{q.content}</p>

                {q.type === 'multiple_choice' && q.choices && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12 }}>
                    {q.choices.map((c, i) => {
                      const letter = String.fromCharCode(65 + i);
                      const selected = answers[q.id] === letter;
                      return (
                        <label key={letter} style={{
                          cursor: 'pointer',
                          background: selected ? 'linear-gradient(135deg, var(--amber-400), var(--amber-600))' : '#fff',
                          color: selected ? '#fff' : 'var(--slate-900)',
                          padding: 16, borderRadius: 'var(--radius-md)',
                          boxShadow: selected ? 'var(--shadow-clay-md)' : 'var(--shadow-clay-sm)',
                          display: 'flex', alignItems: 'center', gap: 10, fontWeight: 600,
                          transition: 'var(--button-transition)',
                        }}>
                          <input type="radio" name={q.id} value={letter} checked={selected}
                                 onChange={() => setAnswers(p => ({ ...p, [q.id]: letter }))}
                                 style={{ accentColor: 'var(--color-primary)' }} />
                          <span><strong>{letter}.</strong> {c}</span>
                        </label>
                      );
                    })}
                  </div>
                )}

                {q.type === 'numeric' && (
                  <input type="text" inputMode="numeric" placeholder="Nhập đáp số..."
                         value={answers[q.id] ?? ''}
                         onChange={e => setAnswers(p => ({ ...p, [q.id]: e.target.value }))}
                         aria-label={`Đáp số câu ${q.index}`}
                         style={{
                           width: '100%', padding: 16, fontSize: 18,
                           fontFamily: 'var(--font-body)',
                           border: '2px solid var(--color-border)',
                           borderRadius: 'var(--radius-md)',
                           boxShadow: 'var(--shadow-clay-inset)',
                           background: '#fff',
                         }} />
                )}

                {q.type === 'essay' && (
                  <textarea rows={6} placeholder="Trình bày lời giải của em..."
                            value={answers[q.id] ?? ''}
                            onChange={e => setAnswers(p => ({ ...p, [q.id]: e.target.value }))}
                            aria-label={`Lời giải câu ${q.index}`}
                            style={{
                              width: '100%', padding: 16, fontSize: 16,
                              fontFamily: 'var(--font-body)',
                              border: '2px solid var(--color-border)',
                              borderRadius: 'var(--radius-md)',
                              boxShadow: 'var(--shadow-clay-inset)',
                              background: '#fff', resize: 'vertical',
                            }} />
                )}
              </Card>
            ))}

            <div style={{ marginTop: 20, textAlign: 'center' }}>
              <Button variant="accent" size="lg" onClick={handleSubmit} loading={submitting}>
                Nộp bài ✨
              </Button>
            </div>
          </div>
        )}
      </main>
    </>
  );
}

function ResultView({ result, examId }: { result: Submission; examId: string }) {
  const { user } = useAuth();
  return (
    <>
      <Navbar label="Kết quả" />
      <main style={{ maxWidth: 900, margin: '0 auto', padding: '40px 24px' }}>
        <div style={{ textAlign: 'center', marginBottom: 32, position: 'relative' }} className="celebrate">
          <div style={{ fontSize: 60 }} aria-hidden="true">🎉</div>
          <h1 style={{ fontSize: 40, marginTop: 8 }}>Nộp bài thành công!</h1>
          <p style={{ fontSize: 24, marginTop: 12 }}>
            Điểm: <strong style={{ color: 'var(--color-primary)' }}>
              {result.total_score.toFixed(1)} / {result.max_total_score.toFixed(1)}
            </strong>{' '}
            ({result.percentage.toFixed(0)}%)
          </p>
          {!result.counts_for_ranking && <Badge variant="warning">Làm bù — không tính ranking</Badge>}
        </div>

        <Card>
          <CardTitle>📋 Chi tiết từng câu</CardTitle>
          <ul style={{ listStyle: 'none', marginTop: 20, display: 'flex', flexDirection: 'column', gap: 10 }}>
            {result.question_results.map((r) => (
              <li key={r.question_id} style={{
                padding: 16,
                background: r.is_correct ? 'var(--green-100)' : '#FEE2E2',
                borderRadius: 'var(--radius-md)',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong>{r.question_id.toUpperCase()}</strong>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                    <span>{r.score.toFixed(2)} / {r.max_score.toFixed(2)}</span>
                    <span aria-hidden="true">{r.is_correct ? '✓' : '✗'}</span>
                    {!r.is_correct && (
                      <AppealButton submissionId={result.id} questionId={r.question_id} token={user?.access_token ?? ''} />
                    )}
                  </div>
                </div>
                {r.feedback && (
                  <div style={{ fontSize: 14, marginTop: 8, color: 'var(--slate-700)' }}>{r.feedback}</div>
                )}
              </li>
            ))}
          </ul>
        </Card>

        <div style={{ textAlign: 'center', marginTop: 32, display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link href="/dashboard"><Button variant="primary" size="lg">Về trang chủ</Button></Link>
          <Link href="/history"><Button variant="ghost" size="lg">Xem lịch sử</Button></Link>
        </div>
      </main>
    </>
  );
}

function AppealButton({ submissionId, questionId, token }: { submissionId: string; questionId: string; token: string }) {
  const [opened, setOpened] = React.useState(false);
  const [reason, setReason] = React.useState('');
  const [done, setDone] = React.useState(false);
  const [loading, setLoading] = React.useState(false);

  async function handleAppeal() {
    if (reason.trim().length < 3) return;
    setLoading(true);
    try {
      await api.appeal(token, submissionId, questionId, reason);
      setDone(true);
    } catch { /* ignore */ }
    finally { setLoading(false); }
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
    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
      <input value={reason} onChange={e => setReason(e.target.value)} placeholder="Lý do..."
             style={{ padding: 6, border: '1px solid var(--color-border)', borderRadius: 8 }} />
      <Button size="sm" variant="accent" onClick={handleAppeal} loading={loading}>Gửi</Button>
    </div>
  );
}
