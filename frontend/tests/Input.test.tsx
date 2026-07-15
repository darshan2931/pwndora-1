import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Input, Textarea, Select } from '@/components/ui/Input';

describe('Input', () => {
  it('renders with label', () => {
    render(<Input label="Email" placeholder="Enter email" />);
    expect(screen.getByLabelText('Email')).toBeDefined();
  });

  it('shows error message', () => {
    render(<Input label="Email" error="Required field" />);
    expect(screen.getByText('Required field')).toBeDefined();
    expect(screen.getByRole('alert')).toBeDefined();
  });

  it('shows hint message', () => {
    render(<Input label="Email" hint="We won't share this" />);
    expect(screen.getByText("We won't share this")).toBeDefined();
  });

  it('sets aria-invalid on error', () => {
    render(<Input error="Error" />);
    const input = screen.getByRole('textbox');
    expect(input.getAttribute('aria-invalid')).toBe('true');
  });
});

describe('Textarea', () => {
  it('renders with label', () => {
    render(<Textarea label="Bio" />);
    expect(screen.getByLabelText('Bio')).toBeDefined();
  });

  it('shows error', () => {
    render(<Textarea error="Too long" />);
    expect(screen.getByText('Too long')).toBeDefined();
  });
});

describe('Select', () => {
  const options = [
    { value: 'soc', label: 'SOC Analyst' },
    { value: 'pentest', label: 'Pen Tester' },
  ];

  it('renders with options', () => {
    render(<Select label="Career" options={options} />);
    expect(screen.getByText('SOC Analyst')).toBeDefined();
    expect(screen.getByText('Pen Tester')).toBeDefined();
  });

  it('renders placeholder', () => {
    render(<Select label="Career" options={options} placeholder="Choose..." />);
    expect(screen.getByText('Choose...')).toBeDefined();
  });
});
