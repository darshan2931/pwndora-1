import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AssessPage from '@/app/assess/page';

const mockAnalyzeCareer = vi.fn();
const mockSaveAssessment = vi.fn();
vi.mock('@/services/api', () => ({
  analyzeCareer: (...args: unknown[]) => mockAnalyzeCareer(...args),
  saveAssessment: (...args: unknown[]) => mockSaveAssessment(...args),
}));

const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: vi.fn(),
    back: vi.fn(),
    prefetch: vi.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/',
}));

describe('AssessPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it('renders the page title', () => {
    render(<AssessPage />);
    expect(screen.getByText('Career Assessment')).toBeDefined();
    expect(screen.getByText('Choose your target career to get started.')).toBeDefined();
  });

  it('displays all career options', () => {
    render(<AssessPage />);
    expect(screen.getByText('SOC Analyst')).toBeDefined();
    expect(screen.getByText('Penetration Tester')).toBeDefined();
    expect(screen.getByText('Cloud Security Engineer')).toBeDefined();
  });

  it('navigates to skills step when career is selected', async () => {
    render(<AssessPage />);
    fireEvent.click(screen.getByText('SOC Analyst'));
    await waitFor(() => {
      expect(screen.getByText('Enter Your Skills')).toBeDefined();
    });
  });

  it('shows back button on skills step', async () => {
    render(<AssessPage />);
    fireEvent.click(screen.getByText('SOC Analyst'));
    await waitFor(() => {
      expect(screen.getByText('Back to career selection')).toBeDefined();
    });
  });

  it('validates empty skills submission', async () => {
    render(<AssessPage />);
    fireEvent.click(screen.getByText('SOC Analyst'));
    await waitFor(() => {
      expect(screen.getByText('Enter Your Skills')).toBeDefined();
    });
    fireEvent.click(screen.getByText('Analyze My Skills'));
    await waitFor(() => {
      expect(screen.getByText(/at least one skill/i)).toBeDefined();
    });
  });

  it('submits skills and shows loading state', async () => {
    mockAnalyzeCareer.mockReturnValue(new Promise(() => {}));
    render(<AssessPage />);
    fireEvent.click(screen.getByText('SOC Analyst'));
    await waitFor(() => {
      expect(screen.getByText('Enter Your Skills')).toBeDefined();
    });
    const textarea = screen.getByPlaceholderText(/e\.g\. Linux/);
    fireEvent.change(textarea, { target: { value: 'Linux, Python' } });
    fireEvent.click(screen.getByText('Analyze My Skills'));
    await waitFor(() => {
      expect(screen.getByText('Analyzing Your Profile')).toBeDefined();
    });
  });

  it('redirects to dashboard on successful analysis', async () => {
    mockAnalyzeCareer.mockResolvedValue({
      success: true,
      data: {
        career_goal: 'SOC Analyst',
        career_readiness: 75,
        matched_skills: ['Linux'],
        missing_skills: ['SIEM'],
        estimated_weeks: 10,
        roadmap: [],
      },
    });
    mockSaveAssessment.mockResolvedValue({ success: true, data: { assessment_id: 'new-id' } });
    render(<AssessPage />);
    fireEvent.click(screen.getByText('SOC Analyst'));
    await waitFor(() => expect(screen.getByText('Enter Your Skills')).toBeDefined());
    fireEvent.change(screen.getByPlaceholderText(/e\.g\. Linux/), { target: { value: 'Linux' } });
    fireEvent.click(screen.getByText('Analyze My Skills'));
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });
});
