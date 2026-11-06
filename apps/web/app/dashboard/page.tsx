import Link from 'next/link';
import { Navbar } from '@/components/Navbar';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { StatCard } from '@/components/StatCard';
import { Badge } from '@/components/Badge';
import { Button } from '@/components/Button';

const strongTopics = [
  { name: 'Trung bình cộng', score: 9.2 },
  { name: 'Phân số', score: 8.8 },
  { name: 'Tỉ số phần trăm', score: 8.5 },
];
const weakTopics = [
  { name: 'Dirichlet', score: 4.2 },
  { name: 'Chuyển động', score: 5.0 },
  { name: 'Bất biến', score: 5.5 },
];

export default function DashboardPage() {
  return (
    <>
      <Navbar userName="Nam" schoolName="THCS Cầu Giấy" />
      <main style={{ maxWidth: 1180, margin: '0 auto', padding: 'var(--spacing-10) var(--spacing-6)' }}>
        <div style={{ marginBottom: 32 }}>
          <Badge variant="info">Thứ 6, 06/11/2026</Badge>
          <h1 style={{ fontSize: 40, marginTop: 12 }}>Chào Nam! Sẵn sàng học hôm nay chưa? 🚀</h1>
          <p style={{ color: 'var(--color-muted-fg)', marginTop: 8, fontSize: 18 }}>
            Đề thi hôm nay đã sẵn sàng. Mở cổng từ 8:00 sáng.
          </p>
        </div>

        {/* Stats grid */}
        <section
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 'var(--spacing-6)',
            marginBottom: 'var(--spacing-10)',
          }}
          aria-label="Thống kê tổng quan"
        >
          <StatCard label="Đề đã làm" value={47} icon="📘" tone="primary" trend="+3 tuần này" />
          <StatCard label="Điểm trung bình" value="7.8" icon="⭐" tone="secondary" trend="+0.4" />
          <StatCard label="Streak liên tiếp" value="12" icon="🔥" tone="accent" />
          <StatCard label="Hạng trong lớp" value="#5" icon="🏆" tone="success" trend="+2 bậc" />
        </section>

        {/* CTA — today's exam */}
        <Card tone="primary" elevated style={{ marginBottom: 'var(--spacing-10)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 20 }}>
            <div>
              <CardTitle>📝 Đề thi hôm nay đã sẵn sàng!</CardTitle>
              <CardDescription>
                10 câu · 60 phút · Bao gồm trung bình cộng, hình học, phân số
              </CardDescription>
              <div style={{ marginTop: 12, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                <Badge variant="info">Mở lúc 8:00</Badge>
                <Badge variant="warning">Đóng lúc 9:00</Badge>
                <Badge variant="success">Kết quả 9:30</Badge>
              </div>
            </div>
            <Link href="/exam">
              <Button variant="primary" size="lg">
                Vào làm bài →
              </Button>
            </Link>
          </div>
        </Card>

        {/* Topic sections */}
        <section
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: 'var(--spacing-6)',
          }}
        >
          <Card>
            <CardTitle>⭐ Chuyên đề bạn giỏi</CardTitle>
            <CardDescription>Những chuyên đề bạn đang làm rất tốt</CardDescription>
            <ul style={{ listStyle: 'none', marginTop: 20, display: 'flex', flexDirection: 'column', gap: 10 }}>
              {strongTopics.map((t) => (
                <li
                  key={t.name}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    padding: 12,
                    background: 'var(--color-blue-50)',
                    borderRadius: 'var(--radius-md)',
                  }}
                >
                  <span style={{ fontWeight: 600 }}>{t.name}</span>
                  <Badge variant="success">{t.score}/10</Badge>
                </li>
              ))}
            </ul>
          </Card>

          <Card>
            <CardTitle>⚠️ Chuyên đề cần luyện</CardTitle>
            <CardDescription>Dành 10 phút mỗi ngày để giỏi hơn!</CardDescription>
            <ul style={{ listStyle: 'none', marginTop: 20, display: 'flex', flexDirection: 'column', gap: 10 }}>
              {weakTopics.map((t) => (
                <li
                  key={t.name}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    padding: 12,
                    background: '#FEF3C7',
                    borderRadius: 'var(--radius-md)',
                  }}
                >
                  <span style={{ fontWeight: 600 }}>{t.name}</span>
                  <Badge variant="warning">{t.score}/10</Badge>
                </li>
              ))}
            </ul>
          </Card>
        </section>
      </main>
    </>
  );
}
