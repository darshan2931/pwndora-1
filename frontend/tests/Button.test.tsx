import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Button from '@/components/ui/Button';

describe('Button', () => {
  it('renders children text', () => {
    render(<Button>Click Me</Button>);
    expect(screen.getByText('Click Me')).toBeDefined();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    fireEvent.click(screen.getByText('Click'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    const btn = screen.getByText('Disabled');
    expect(btn.hasAttribute('disabled')).toBe(true);
  });

  it('is disabled when loading', () => {
    render(<Button loading>Loading</Button>);
    const btn = screen.getByText('Loading');
    expect(btn.hasAttribute('disabled')).toBe(true);
  });

  it('applies variant classes', () => {
    const { rerender } = render(<Button variant="primary">Test</Button>);
    expect(screen.getByText('Test').className).toContain('bg-primary');

    rerender(<Button variant="danger">Test</Button>);
    expect(screen.getByText('Test').className).toContain('bg-error');

    rerender(<Button variant="outline">Test</Button>);
    expect(screen.getByText('Test').className).toContain('border-primary');
  });

  it('applies size classes', () => {
    const { rerender } = render(<Button size="sm">Test</Button>);
    expect(screen.getByText('Test').className).toContain('px-3');

    rerender(<Button size="lg">Test</Button>);
    expect(screen.getByText('Test').className).toContain('px-7');
  });

  it('applies fullWidth class', () => {
    render(<Button fullWidth>Test</Button>);
    expect(screen.getByText('Test').className).toContain('w-full');
  });
});
