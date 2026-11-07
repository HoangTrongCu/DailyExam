import '@testing-library/jest-dom';
import { cn, formatDateVi, formatDuration, formatScore, gradeLetter, percentage } from '@/lib/utils';

describe('cn', () => {
  it('joins', () => expect(cn('a', 'b')).toBe('a b'));
  it('skips falsy', () => expect(cn('a', false, null, 'b')).toBe('a b'));
  it('objects', () => expect(cn({ a: true, b: false })).toBe('a'));
});

describe('formatScore', () => {
  it('normal', () => expect(formatScore(7.5, 10)).toBe('7.5 / 10.0'));
  it('zero max', () => expect(formatScore(0, 0)).toBe('0 / 0'));
});

describe('percentage', () => {
  it('normal', () => expect(percentage(7.5, 10)).toBe(75));
  it('zero', () => expect(percentage(5, 0)).toBe(0));
});

describe('gradeLetter', () => {
  it.each([[95,'A'],[80,'B'],[65,'C'],[45,'D'],[30,'F']])('for %i returns %s', (p, l) => {
    expect(gradeLetter(p)).toBe(l);
  });
});

describe('formatDateVi', () => {
  it('pads', () => expect(formatDateVi(new Date(2026, 10, 6))).toBe('06/11/2026'));
  it('day', () => expect(formatDateVi(new Date(2026, 0, 3))).toBe('03/01/2026'));
});

describe('formatDuration', () => {
  it('zero', () => expect(formatDuration(0)).toBe('00:00'));
  it('with minutes', () => expect(formatDuration(65)).toBe('01:05'));
  it('negative clamp', () => expect(formatDuration(-5)).toBe('00:00'));
  it('floor', () => expect(formatDuration(5.9)).toBe('00:05'));
});
