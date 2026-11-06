import Link from 'next/link';
import { Button } from '@/components/Button';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { Badge } from '@/components/Badge';

const features = [
  {
    icon: '✨',
    title: 'Đề thi mỗi ngày',
    desc: 'Tự động sinh 1 đề mới lúc 5h sáng, mở cổng lúc 8h để bạn luyện tập.',
  },
  {
    icon: '🎯',
    title: 'Chấm bài siêu nhanh',
    desc: 'Nhận kết quả và lời giải chi tiết chỉ sau vài giây khi nộp bài.',
  },
  {
    icon: '📊',
    title: 'Thống kê thông minh',
    desc: 'Biết chuyên đề nào bạn mạnh, chuyên đề nào cần luyện thêm.',
  },
  {
    icon: '🏆',
    title: 'Thi đua cùng lớp',
    desc: 'Xem thứ hạng và so sánh với các bạn cùng trường.',
  },
];

export default function LandingPage() {
  return (
    <main style={{ maxWidth: 1180, margin: '0 auto', padding: 'var(--spacing-12) var(--spacing-6)' }}>
      {/* Hero */}
      <section
        style={{
          display: 'grid',
          gridTemplateColumns: '1.1fr 0.9fr',
          gap: 'var(--spacing-10)',
          alignItems: 'center',
          marginBottom: 'var(--spacing-16)',
        }}
      >
        <div>
          <Badge variant="info">🎉 Mới ra mắt cho THCS Cầu Giấy</Badge>
          <h1
            style={{
              fontSize: 56,
              lineHeight: 1.1,
              marginTop: 24,
              marginBottom: 20,
              background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent))',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            Mỗi ngày một đề, luyện thi vui hơn!
          </h1>
          <p style={{ fontSize: 20, color: 'var(--color-slate-600)', marginBottom: 32, maxWidth: 520 }}>
            DailyExam giúp bạn luyện thi tuyển sinh dễ dàng với đề thi tự động mỗi ngày, chấm bài siêu nhanh và
            lời giải dễ hiểu.
          </p>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
            <Link href="/dashboard">
              <Button variant="primary" size="lg">
                Bắt đầu học ngay 🚀
              </Button>
            </Link>
            <Link href="/exam">
              <Button variant="ghost" size="lg">
                Xem đề hôm nay
              </Button>
            </Link>
          </div>
        </div>

        {/* Hero illustration */}
        <div
          aria-hidden="true"
          style={{
            position: 'relative',
            height: 420,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <div
            style={{
              width: 320,
              height: 320,
              background: 'linear-gradient(135deg, var(--color-blue-400), var(--color-accent))',
              borderRadius: '50%',
              filter: 'blur(60px)',
              opacity: 0.4,
              position: 'absolute',
            }}
          />
          <div
            style={{
              background: '#fff',
              borderRadius: 'var(--radius-3xl)',
              padding: 32,
              boxShadow: 'var(--shadow-clay-lg)',
              width: 320,
              position: 'relative',
              transform: 'rotate(-4deg)',
            }}
          >
            <div style={{ fontSize: 14, color: 'var(--color-muted-fg)', marginBottom: 8 }}>Thứ 5 • 06/11/2026</div>
            <div style={{ fontSize: 24, fontFamily: 'var(--font-heading)', fontWeight: 700 }}>
              Đề Toán hôm nay
            </div>
            <div style={{ marginTop: 20, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <Badge variant="info">10 câu</Badge>
              <Badge variant="warning">60 phút</Badge>
              <Badge variant="success">Mở lúc 8h</Badge>
            </div>
            <div
              style={{
                marginTop: 24,
                padding: 16,
                background: 'var(--color-blue-50)',
                borderRadius: 'var(--radius-lg)',
                fontSize: 14,
              }}
            >
              <strong>Chuyên đề:</strong> Trung bình cộng, Tỉ số phần trăm, Hình học...
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section style={{ marginBottom: 'var(--spacing-16)' }}>
        <h2 style={{ fontSize: 36, textAlign: 'center', marginBottom: 48 }}>Tại sao chọn DailyExam?</h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: 'var(--spacing-6)',
          }}
        >
          {features.map((f) => (
            <Card key={f.title}>
              <div
                aria-hidden="true"
                style={{
                  fontSize: 40,
                  width: 72,
                  height: 72,
                  borderRadius: 'var(--radius-xl)',
                  background: 'linear-gradient(135deg, var(--color-blue-100), var(--color-pink-100))',
                  display: 'grid',
                  placeItems: 'center',
                  marginBottom: 20,
                }}
              >
                {f.icon}
              </div>
              <CardTitle>{f.title}</CardTitle>
              <CardDescription>{f.desc}</CardDescription>
            </Card>
          ))}
        </div>
      </section>

      <footer style={{ textAlign: 'center', padding: 24, color: 'var(--color-muted-fg)' }}>
        © 2026 DailyExam · Luyện thi dễ dàng, kết quả vững vàng
      </footer>
    </main>
  );
}
