import type { Metadata, Viewport } from 'next';
import '../styles/globals.css';
import { AuthProvider } from '@/components/AuthProvider';

export const metadata: Metadata = {
  title: 'DailyExam — Luyện thi mỗi ngày',
  description:
    'Nền tảng tự động sinh đề và chấm bài thông minh cho học sinh tiểu học và THCS. Mỗi ngày một đề mới, luyện thi hiệu quả.',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#2563EB',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
