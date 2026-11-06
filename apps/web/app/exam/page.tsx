'use client';

import React from 'react';
import { Navbar } from '@/components/Navbar';
import { Card, CardTitle } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Button } from '@/components/Button';
import { CountdownTimer } from '@/components/CountdownTimer';

const sampleQuestions = [
  {
    id: 'q1',
    index: 1,
    type: 'mcq' as const,
    content:
      'Có 1500 du khách được hỏi. 25% thích phở, 18% thích bánh cuốn, 43% thích bún chả, còn lại thích bánh mỳ. Hỏi bao nhiêu người thích bánh mỳ?',
    choices: ['180', '195', '210', '225'],
    score: 0.75,
  },
  {
    id: 'q2',
    index: 2,
    type: 'numeric' as const,
    content:
      'Trung bình cộng của ba số là 25. Số thứ nhất là 20, số thứ hai là 28. Tìm số thứ ba.',
    score: 1.0,
  },
  {
    id: 'q3',
    index: 3,
    type: 'essay' as const,
    content: 'Trình bày cách giải bài toán ở câu 2.',
    score: 1.5,
  },
];

export default function ExamPage() {
  const [answers, setAnswers] = React.useState<Record<string, string>>({});
  const [submitted, setSubmitted] = React.useState(false);

  const handleChange = (qid: string, value: string) => {
    setAnswers((prev) => ({ ...prev, [qid]: value }));
  };

  const handleSubmit = () => setSubmitted(true);

  if (submitted) {
    return (
      <>
        <Navbar userName="Nam" />
        <main
          style={{
            maxWidth: 680,
            margin: '0 auto',
            padding: 'var(--spacing-16) var(--spacing-6)',
            textAlign: 'center',
          }}
        >
          <div style={{ fontSize: 80, marginBottom: 20 }} aria-hidden="true">
            🎉
          </div>
          <h1 style={{ fontSize: 40 }}>Nộp bài thành công!</h1>
          <p style={{ fontSize: 18, color: 'var(--color-muted-fg)', marginTop: 12, marginBottom: 32 }}>
            Kết quả sẽ có lúc 9:30 sáng. Hãy kiểm tra lại nhé!
          </p>
          <Button variant="primary" size="lg" onClick={() => window.location.assign('/dashboard')}>
            Về trang chủ
          </Button>
        </main>
      </>
    );
  }

  return (
    <>
      <Navbar userName="Nam" />
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
            <Badge variant="info">Đề ngày 06/11/2026 · THCS Cầu Giấy</Badge>
            <h1 style={{ marginTop: 12, fontSize: 32 }}>Đề thi Toán hôm nay</h1>
          </div>
          <CountdownTimer totalSeconds={60 * 60} />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {sampleQuestions.map((q) => (
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
                <Badge variant={q.type === 'mcq' ? 'info' : q.type === 'numeric' ? 'warning' : 'danger'}>
                  {q.type === 'mcq' ? 'Trắc nghiệm' : q.type === 'numeric' ? 'Điền số' : 'Tự luận'}
                </Badge>
                <Badge variant="default">{q.score.toFixed(2)} điểm</Badge>
              </div>
              <CardTitle>Câu {q.index}</CardTitle>
              <p style={{ fontSize: 17, marginTop: 4, marginBottom: 20, lineHeight: 1.6 }}>{q.content}</p>

              {q.type === 'mcq' && q.choices && (
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
                          border: '2px solid transparent',
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
                          onChange={() => handleChange(q.id, letter)}
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
                  onChange={(e) => handleChange(q.id, e.target.value)}
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
                  onChange={(e) => handleChange(q.id, e.target.value)}
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
        </div>

        <div style={{ marginTop: 40, textAlign: 'center' }}>
          <Button variant="accent" size="lg" onClick={handleSubmit}>
            Nộp bài ✨
          </Button>
        </div>
      </main>
    </>
  );
}
