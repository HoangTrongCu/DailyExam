import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import { Navbar } from '@/components/Navbar';

// Mock next/link to a plain anchor
jest.mock('next/link', () => ({ __esModule: true, default: ({ children, href, ...rest }: any) => (
  <a href={href} {...rest}>{children}</a>
) }));

describe('Navbar', () => {
  it('renders default school name', () => {
    render(<Navbar />);
    expect(screen.getByText('THCS Cầu Giấy')).toBeInTheDocument();
  });

  it('renders with custom user name initial', () => {
    render(<Navbar userName="Minh" />);
    expect(screen.getByLabelText(/User Minh/i)).toHaveTextContent('M');
  });

  it('renders nav links', () => {
    render(<Navbar />);
    expect(screen.getByText('Trang chủ')).toBeInTheDocument();
    expect(screen.getByText('Đề hôm nay')).toBeInTheDocument();
  });
});
