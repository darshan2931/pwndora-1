import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Skeleton, { SkeletonCard, SkeletonDashboard } from '@/components/ui/Skeleton';

describe('Skeleton', () => {
  it('renders text variant by default', () => {
    const { container } = render(<Skeleton />);
    expect(container.firstChild).toBeDefined();
  });

  it('renders circular variant', () => {
    const { container } = render(<Skeleton variant="circular" width="40px" height="40px" />);
    const el = container.firstChild as HTMLElement;
    expect(el.className).toContain('rounded-full');
  });

  it('renders rectangular variant', () => {
    const { container } = render(<Skeleton variant="rectangular" />);
    const el = container.firstChild as HTMLElement;
    expect(el.className).toContain('rounded-lg');
  });
});

describe('SkeletonCard', () => {
  it('renders placeholder content', () => {
    const { container } = render(<SkeletonCard />);
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });
});

describe('SkeletonDashboard', () => {
  it('renders dashboard skeleton layout', () => {
    const { container } = render(<SkeletonDashboard />);
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });
});
