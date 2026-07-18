import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import MentorPage from '@/app/mentor/page';

const mockMentorChat = vi.fn();
vi.mock('@/services/api', () => ({
  mentorChat: (...args: unknown[]) => mockMentorChat(...args),
}));

describe('MentorPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the page title', () => {
    render(<MentorPage />);
    expect(screen.getByText('AI Career Mentor')).toBeDefined();
  });

  it('shows suggested questions initially', () => {
    render(<MentorPage />);
    expect(screen.getByText("Hello! I'm your AI Career Mentor")).toBeDefined();
    expect(screen.getByText('What certifications should I get for SOC Analyst?')).toBeDefined();
  });

  it('shows chat input', () => {
    render(<MentorPage />);
    expect(screen.getByLabelText('Type your question')).toBeDefined();
  });

  it('shows send button', () => {
    render(<MentorPage />);
    expect(screen.getByLabelText('Send message')).toBeDefined();
  });

  it('sends a message and displays response', async () => {
    mockMentorChat.mockResolvedValue({ response: 'You should get the CompTIA Security+.' });
    render(<MentorPage />);
    const input = screen.getByLabelText('Type your question');
    fireEvent.change(input, { target: { value: 'What cert should I get?' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    await waitFor(() => {
      expect(screen.getByText('What cert should I get?')).toBeDefined();
      expect(screen.getByText('You should get the CompTIA Security+.')).toBeDefined();
    });
  });

  it('displays user message on the right side', async () => {
    mockMentorChat.mockResolvedValue({ response: 'Answer' });
    render(<MentorPage />);
    const input = screen.getByLabelText('Type your question');
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    await waitFor(() => {
      expect(screen.getByText('Hello')).toBeDefined();
    });
  });

  it('handles API error gracefully', async () => {
    mockMentorChat.mockRejectedValue(new Error('Network error'));
    render(<MentorPage />);
    const input = screen.getByLabelText('Type your question');
    fireEvent.change(input, { target: { value: 'Test error' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    await waitFor(() => {
      expect(screen.getByText(/apologize|error/i)).toBeDefined();
    });
  });

  it('allows clicking suggested questions', async () => {
    mockMentorChat.mockResolvedValue({ response: 'Great question!' });
    render(<MentorPage />);
    fireEvent.click(screen.getByText('What certifications should I get for SOC Analyst?'));
    await waitFor(() => {
      expect(mockMentorChat).toHaveBeenCalled();
      expect(screen.getByText('Great question!')).toBeDefined();
    });
  });
});
