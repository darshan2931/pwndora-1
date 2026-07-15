import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Home from '@/app/page';

describe('Home Page', () => {
  it('renders the hero heading', () => {
    render(<Home />);
    expect(screen.getByText(/Your Personalized Path to a/)).toBeDefined();
    expect(screen.getByText('Cybersecurity Career')).toBeDefined();
  });

  it('renders AI-Powered badge', () => {
    render(<Home />);
    expect(screen.getByText('AI-Powered Career Intelligence')).toBeDefined();
  });

  it('has Explore Careers and Upload Resume buttons', () => {
    render(<Home />);
    expect(screen.getByText('Explore Careers')).toBeDefined();
    expect(screen.getByText('Upload Resume')).toBeDefined();
  });

  it('renders How It Works section', () => {
    render(<Home />);
    expect(screen.getByText('How It Works')).toBeDefined();
    expect(screen.getByText('Upload Your Resume')).toBeDefined();
    expect(screen.getByText('Get Your Assessment')).toBeDefined();
    expect(screen.getByText('Follow Your Roadmap')).toBeDefined();
    expect(screen.getByText('Grow Your Career')).toBeDefined();
  });

  it('renders features section', () => {
    render(<Home />);
    expect(screen.getByText('Everything You Need')).toBeDefined();
    expect(screen.getByText('Resume Intelligence')).toBeDefined();
    expect(screen.getByText('Career Intelligence')).toBeDefined();
    expect(screen.getByText('Personalized Roadmap')).toBeDefined();
    expect(screen.getByText('AI Career Mentor')).toBeDefined();
  });

  it('renders CTA section', () => {
    render(<Home />);
    expect(screen.getByText('Ready to Start Your Journey?')).toBeDefined();
    expect(screen.getByText('Get Started Now')).toBeDefined();
    expect(screen.getByText('Browse Careers')).toBeDefined();
  });
});
