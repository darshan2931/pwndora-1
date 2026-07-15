import { describe, it, expect } from 'vitest';
import { SUPPORTED_CAREERS, READINESS_THRESHOLDS, DIFFICULTY_COLORS, MENTOR_SUGGESTED_QUESTIONS } from '@/constants';

describe('Constants', () => {
  it('has 6 supported careers', () => {
    expect(SUPPORTED_CAREERS).toHaveLength(6);
  });

  it('each career has id and title', () => {
    SUPPORTED_CAREERS.forEach(career => {
      expect(career.id).toBeDefined();
      expect(career.title).toBeDefined();
      expect(typeof career.id).toBe('string');
      expect(typeof career.title).toBe('string');
    });
  });

  it('has readiness thresholds', () => {
    expect(READINESS_THRESHOLDS.low).toBe(40);
    expect(READINESS_THRESHOLDS.medium).toBe(70);
  });

  it('has difficulty colors for all levels', () => {
    expect(DIFFICULTY_COLORS.beginner).toBeDefined();
    expect(DIFFICULTY_COLORS.intermediate).toBeDefined();
    expect(DIFFICULTY_COLORS.advanced).toBeDefined();
    expect(DIFFICULTY_COLORS.easy).toBeDefined();
    expect(DIFFICULTY_COLORS.medium).toBeDefined();
    expect(DIFFICULTY_COLORS.hard).toBeDefined();
  });

  it('has mentor suggested questions', () => {
    expect(MENTOR_SUGGESTED_QUESTIONS.length).toBeGreaterThan(0);
    MENTOR_SUGGESTED_QUESTIONS.forEach(q => {
      expect(typeof q).toBe('string');
      expect(q.length).toBeGreaterThan(10);
    });
  });
});
