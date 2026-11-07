import type { Metadata, Viewport } from 'next';
import '../styles/globals.css';
import { AuthProvider } from '@/components/AuthProvider';

export const metadata: Metadata = {
  title: 'DailyExam — Luyện thi mỗi ngày',
  description: 'Tự động sinh đề và chấm bài giúp HS lớp 5 luyện thi tuyển sinh lớp 6 CLC.',
};

export const viewport: Viewport = {
  width: 'device-width', initialScale: 1, themeColor: '#D97706',
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
