import Link from 'next/link';
import { Button } from '@/components/Button';
import { Card, CardTitle, CardDescription } from '@/components/Card';
import { Badge } from '@/components/Badge';

const FEATURES = [
  { icon: '✨', title: 'Mỗi ngày 1 đề mới', desc: 'Tự động sinh đề 5h sáng, HS làm trong ngày.' },
  { icon: '🎯', title: 'Chấm cả tự luận', desc: 'AI chấm tự luận có phúc khảo, công bằng với HS.' },
  { icon: '🏆', title: 'Ranking 3 cấp', desc: 'Thi đua theo đề, theo tuần, theo tổng — có quà.' },
  { icon: '📊', title: 'Thấy tiến bộ', desc: 'Email tuần cho PH, chuyên đề mạnh/yếu cho HS.' },
];

export default function LandingPage() {
  return (
    <main style={{ maxWidth: 1180, margin: '0 auto', padding: '48px 24px' }}>
      <section style={{
        display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: 40, alignItems: 'center', marginBottom: 64,
      }}>
        <div>
          <Badge variant="info">🎉 Pilot cho THCS Cầu Giấy</Badge>
          <h1 style={{
            fontSize: 'clamp(40px, 6vw, 60px)', lineHeight: 1.1,
            marginTop: 24, marginBottom: 20,
            background: 'linear-gradient(135deg, var(--amber-600), var(--green-600))',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
          }}>
            Luyện thi vui hơn,<br />tiến bộ nhanh hơn 🚀
          </h1>
          <p style={{ fontSize: 20, color: 'var(--slate-600)', marginBottom: 32, maxWidth: 520 }}>
            Nền tảng duy nhất mang đến <strong>đề thi chuẩn từng trường chất lượng cao</strong>,
            chấm cả tự luận và cho PH thấy rõ sự tiến bộ của con.
          </p>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
            <Link href="/register"><Button variant="primary" size="lg">Đăng ký miễn phí</Button></Link>
            <Link href="/login"><Button variant="ghost" size="lg">Đăng nhập</Button></Link>
          </div>
        </div>

        <div aria-hidden="true" style={{
          position: 'relative', minHeight: 420,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <div style={{
            width: 320, height: 320,
            background: 'linear-gradient(135deg, var(--amber-400), var(--green-500))',
            borderRadius: '50%', filter: 'blur(60px)', opacity: 0.4,
            position: 'absolute',
          }} />
          <Card elevated style={{ width: 340, transform: 'rotate(-3deg)' }}>
            <div style={{ fontSize: 14, color: 'var(--color-muted-fg)', marginBottom: 8 }}>
              Thứ 7 · {new Date().toLocaleDateString('vi-VN')}
            </div>
            <CardTitle>📝 Đề Toán hôm nay</CardTitle>
            <div style={{ marginTop: 16, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <Badge variant="info">10 câu</Badge>
              <Badge variant="warning">60 phút</Badge>
              <Badge variant="success">Chấm tự động</Badge>
            </div>
            <div style={{
              marginTop: 20, padding: 14,
              background: 'var(--amber-50)',
              borderRadius: 'var(--radius-md)',
              fontSize: 14,
            }}>
              <strong>TBC</strong>, Phần trăm, Hình học, Phân số, Chuyển động...
            </div>
          </Card>
        </div>
      </section>

      <section style={{ marginBottom: 64 }}>
        <h2 style={{ fontSize: 36, textAlign: 'center', marginBottom: 48 }}>Vì sao chọn DailyExam?</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 24 }}>
          {FEATURES.map((f) => (
            <Card key={f.title}>
              <div aria-hidden="true" style={{
                fontSize: 40, width: 72, height: 72,
                borderRadius: 'var(--radius-md)',
                background: 'linear-gradient(135deg, var(--amber-100), var(--green-100))',
                display: 'grid', placeItems: 'center', marginBottom: 20,
              }}>{f.icon}</div>
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
