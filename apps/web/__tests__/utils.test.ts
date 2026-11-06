import '@testing-library/jest-dom';
import {
  cn,
  formatScore,
  percentage,
  gradeLetter,
  formatDateVi,
  pluralizeVi,
} from '@/lib/utils';

describe('cn', () => {
  it('joins classes', () => {
    expect(cn('a', 'b')).toBe('a b');
  });
  it('filters falsy', () => {
    expect(cn('a', false, null, undefined, 'b')).toBe('a b');
  });
  it('handles objects', () => {
    expect(cn({ a: true, b: false, c: true })).toBe('a c');
  });
});

describe('formatScore', () => {
  it('formats normal', () => {
    expect(formatScore(7.5, 10)).toBe('7.5 / 10.0');
  });
  it('handles zero max', () => {
    expect(formatScore(0, 0)).toBe('0 / 0');
  });
});

describe('percentage', () => {
  it('computes percent', () => {
    expect(percentage(50, 100)).toBe(50);
    expect(percentage(7.5, 10)).toBe(75);
  });
  it('handles zero max', () => {
    expect(percentage(5, 0)).toBe(0);
  });
});

describe('gradeLetter', () => {
  it.each([
    [95, 'A'],
    [90, 'A'],
    [80, 'B'],
    [75, 'B'],
    [65, 'C'],
    [60, 'C'],
    [50, 'D'],
    [40, 'D'],
    [39, 'F'],
    [0, 'F'],
  ])('for %i returns %s', (percent, letter) => {
    expect(gradeLetter(percent)).toBe(letter);
  });
});

describe('formatDateVi', () => {
  it('formats dd/mm/yyyy', () => {
    expect(formatDateVi(new Date(2026, 10, 6))).toBe('06/11/2026');
  });
  it('pads single digits', () => {
    expect(formatDateVi(new Date(2026, 0, 3))).toBe('03/01/2026');
  });
});

describe('pluralizeVi', () => {
  it('returns count + word', () => {
    expect(pluralizeVi(3, 'câu')).toBe('3 câu');
  });
});
