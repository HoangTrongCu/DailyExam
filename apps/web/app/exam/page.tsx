'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Navbar } from '@/components/Navbar';
import { Card, CardTitle } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Button } from '@/components/Button';
import { CountdownTimer } from '@/components/CountdownTimer';
import { useAuth } from '@/components/AuthProvider';
import { api, type DailyExam, type Submission } from '@/lib/api';

export default function ExamPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [exam, setExam] = React.useState<DailyExam | null>(null);
  const [answers, setAnswers] = React.useState<Record<string, string>>({});
  const [loading, setLoading] = React.useState(true);
  const [submitting, setSubmitting] = React.useState(false);
  const [result, setResult] = React.useState<Submission | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!user) {
      const t = setTimeout(() => router.push('/login'), 200);
      return () => clearTimeout(t);
    }
    const schoolId = user.school_id ?? 'cau_giay';
    const today = new Date().toISOString().slice(0, 10);
    api
      .dailyExam(schoolId, today)
      .then(setExam)
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [user, router]);

  async function handleSubmit() {
    if (!user || !exam) return;
    setSubmitting(true);
    try {
      const sub = await api.submit(user.access_token, exam.id, answers);
      setResult(sub);
    } catch (e) {
      setError(String(e));
    } finally {
      setSubmitting(false);
    }
  }

  if (!user) return null;

  if (result) {
    return <ResultView result={result} />;
  }

  return (
    <>
      <Navbar userName={user.full_name} />
      <main style={{ maxWidth: 880, margin: '0 auto', padding: 'var(--spacing-10) var(--spacing-6)' }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 32,
            flexWrap: 'wrap',
            gap: 16,
          }}
        >
          <div>
            <Badge variant="info">Đề ngày {new Date().toLocaleDateString('vi-VN')} · THCS Cầu Giấy</Badge>
            <h1 style={{ marginTop: 12, fontSize: 32 }}>Đề thi Toán hôm nay</h1>
          </div>
          {exam && <CountdownTimer totalSeconds={(exam.duration_minutes ?? 60) * 60} />}
        </div>

        {loading && <p>Đang tải đề...</p>}
        {error && (
          <Card tone="accent">
            <CardTitle>Không tải được đề</CardTitle>
            <p style={{ marginTop: 8 }}>{error}</p>
          </Card>
        )}

        {exam && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            {exam.questions.map((q) => (
              <Card key={q.id} tone={q.type === 'essay' ? 'accent' : 'default'}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                  <div
                    aria-hidden="true"
                    style={{
                      width: 36,
                      height: 36,
                      borderRadius: 'var(--radius-full)',
                      background: 'linear-gradient(135deg, var(--color-blue-500), var(--color-primary))',
                      color: '#fff',
                      display: 'grid',
                      placeItems: 'center',
                      fontWeight: 700,
                    }}
                  >
                    {q.index}
                  </div>
                  <Badge variant={q.type === 'multiple_choice' ? 'info' : q.type === 'numeric' ? 'warning' : 'danger'}>
                    {q.type === 'multiple_choice' ? 'Trắc nghiệm' : q.type === 'numeric' ? 'Điền số' : 'Tự luận'}
                  </Badge>
                  <Badge variant="default">{q.max_score.toFixed(2)} điểm</Badge>
                  <Badge variant="default">{q.difficulty}</Badge>
                </div>
                <CardTitle>Câu {q.index}</CardTitle>
                <p style={{ fontSize: 17, marginTop: 4, marginBottom: 20, lineHeight: 1.6 }}>{q.content}</p>

                {q.type === 'multiple_choice' && q.choices && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12 }}>
                    {q.choices.map((c, i) => {
                      const letter = String.fromCharCode(65 + i);
                      const selected = answers[q.id] === letter;
                      return (
                        <label
                          key={letter}
                          style={{
                            cursor: 'pointer',
                            background: selected ? 'linear-gradient(135deg, var(--color-blue-500), var(--color-primary))' : '#fff',
                            color: selected ? '#fff' : 'var(--color-foreground)',
                            padding: 16,
                            borderRadius: 'var(--radius-lg)',
                            boxShadow: selected ? 'var(--shadow-clay-md)' : 'var(--shadow-clay-sm)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 10,
                            fontWeight: 600,
                            transition: 'var(--button-transition)',
                          }}
                        >
                          <input
                            type="radio"
                            name={q.id}
                            value={letter}
                            checked={selected}
                            onChange={() => setAnswers((prev) => ({ ...prev, [q.id]: letter }))}
                            style={{ accentColor: 'var(--color-primary)' }}
                          />
                          <span>
                            <strong>{letter}.</strong> {c}
                          </span>
                        </label>
                      );
                    })}
                  </div>
                )}

                {q.type === 'numeric' && (
                  <input
                    type="text"
                    inputMode="numeric"
                    placeholder="Nhập đáp số..."
                    value={answers[q.id] ?? ''}
                    onChange={(e) => setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))}
                    aria-label={`Đáp số câu ${q.index}`}
                    style={{
                      width: '100%',
                      padding: 16,
                      fontSize: 18,
                      fontFamily: 'var(--font-body)',
                      border: '2px solid var(--color-border)',
                      borderRadius: 'var(--radius-lg)',
                      boxShadow: 'var(--shadow-clay-inset)',
                      background: '#fff',
                    }}
                  />
                )}

                {q.type === 'essay' && (
                  <textarea
                    rows={6}
                    placeholder="Trình bày lời giải của em..."
                    value={answers[q.id] ?? ''}
                    onChange={(e) => setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))}
                    aria-label={`Lời giải câu ${q.index}`}
                    style={{
                      width: '100%',
                      padding: 16,
                      fontSize: 16,
                      fontFamily: 'var(--font-body)',
                      border: '2px solid var(--color-border)',
                      borderRadius: 'var(--radius-lg)',
                      boxShadow: 'var(--shadow-clay-inset)',
                      background: '#fff',
                      resize: 'vertical',
                    }}
                  />
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

function ResultView({ result }: { result: Submission }) {
  const { user } = useAuth();
  return (
    <>
      <Navbar userName={user?.full_name ?? 'Học sinh'} />
      <main style={{ maxWidth: 880, margin: '0 auto', padding: 'var(--spacing-10) var(--spacing-6)' }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{ fontSize: 60 }} aria-hidden="true">
            🎉
          </div>
          <h1 style={{ fontSize: 40 }}>Nộp bài thành công!</h1>
          <p style={{ fontSize: 24, marginTop: 12 }}>
            Điểm của bạn:{' '}
            <strong style={{ color: 'var(--color-primary)' }}>
              {result.total_score.toFixed(2)} / {result.max_total_score.toFixed(2)}
            </strong>{' '}
            ({result.percentage.toFixed(0)}%)
          </p>
        </div>

        <Card>
          <CardTitle>📋 Chi tiết từng câu</CardTitle>
          <ul style={{ listStyle: 'none', marginTop: 20, display: 'flex', flexDirection: 'column', gap: 10 }}>
            {result.question_results.map((r) => (
              <li
                key={r.question_id}
                style={{
                  padding: 14,
                  background: r.is_correct ? '#DCFCE7' : '#FEE2E2',
                  borderRadius: 'var(--radius-md)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <strong>{r.question_id.toUpperCase()}</strong>
                  <span>
                    {r.score.toFixed(2)} / {r.max_score.toFixed(2)}{' '}
                    {r.is_correct ? '✓' : '✗'}
                  </span>
                </div>
                {r.feedback && (
                  <div style={{ fontSize: 14, marginTop: 6, color: 'var(--color-slate-700)' }}>{r.feedback}</div>
                )}
              </li>
            ))}
          </ul>
        </Card>

        <div style={{ textAlign: 'center', marginTop: 32 }}>
          <Button variant="primary" size="lg" onClick={() => (window.location.href = '/dashboard')}>
            Về trang chủ
          </Button>
        </div>
      </main>
    </>
  );
}
