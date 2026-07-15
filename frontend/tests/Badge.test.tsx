import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Badge from '@/components/ui/Badge';

describe('Badge', () => {
  it('renders children text', () => {
    render(<Badge>Active</Badge>);
    expect(screen.getByText('Active')).toBeDefined();
  });

  it('applies variant classes', () => {
    const { rerender } = render(<Badge variant="success">Test</Badge>);
    expect(screen.getByText('Test').className).toContain('bg-green-100');

    rerender(<Badge variant="danger">Test</Badge>);
    expect(screen.getByText('Test').className).toContain('bg-red-100');

    rerender(<Badge variant="primary">Test</Badge>);
    expect(screen.getByText('Test').className).toContain('bg-blue-100');
  });

  it('applies size classes', () => {
    const { rerender } = render(<Badge size="sm">Test</Badge>);
    expect(screen.getByText('Test').className).toContain('px-2');

    rerender(<Badge size="lg">Test</Badge>);
    expect(screen.getByText('Test').className).toContain('px-3');
  });

  it('renders dot indicator when dot is true', () => {
    const { container } = render(<Badge dot>Test</Badge>);
    const dot = container.querySelector('.w-1\\.5');
    expect(dot).toBeTruthy();
  });
});
