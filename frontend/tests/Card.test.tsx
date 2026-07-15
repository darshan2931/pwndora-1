import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Card, CardHeader } from '@/components/ui/Card';

describe('Card', () => {
  it('renders children', () => {
    render(<Card><p>Card content</p></Card>);
    expect(screen.getByText('Card content')).toBeDefined();
  });

  it('applies padding', () => {
    const { rerender } = render(<Card padding="sm">Test</Card>);
    expect(screen.getByText('Test').className).toContain('p-4');

    rerender(<Card padding="lg">Test</Card>);
    expect(screen.getByText('Test').className).toContain('p-8');
  });

  it('applies variant', () => {
    const { rerender } = render(<Card variant="default">Test</Card>);
    expect(screen.getByText('Test').className).toContain('bg-white');

    rerender(<Card variant="elevated">Test</Card>);
    expect(screen.getByText('Test').className).toContain('shadow-md');
  });

  it('applies hover styles', () => {
    render(<Card hover>Test</Card>);
    expect(screen.getByText('Test').className).toContain('hover:shadow-md');
  });
});

describe('CardHeader', () => {
  it('renders title', () => {
    render(<CardHeader title="My Title" />);
    expect(screen.getByText('My Title')).toBeDefined();
  });

  it('renders subtitle', () => {
    render(<CardHeader title="Title" subtitle="Subtitle text" />);
    expect(screen.getByText('Subtitle text')).toBeDefined();
  });

  it('renders action element', () => {
    render(<CardHeader title="Title" action={<button>Save</button>} />);
    expect(screen.getByText('Save')).toBeDefined();
  });
});
