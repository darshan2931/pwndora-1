import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import DashboardPage from '@/app/dashboard/page';

const mockGetAssessment = vi.fn();
vi.mock('@/services/api', () => ({
  getAssessment: (...args: unknown[]) => mockGetAssessment(...args),
}));

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it('shows no assessment state when no data', async () => {
    mockGetAssessment.mockRejectedValue(new Error('Not found'));
    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText('No Assessment Found')).toBeDefined();
      expect(screen.getByText('Start Assessment')).toBeDefined();
    });
  });

  it('loads assessment from sessionStorage', async () => {
    const assessmentData = {
      career_goal: 'SOC Analyst',
      career_readiness: 75,
      matched_skills: ['SIEM', 'Linux'],
      missing_skills: ['Kubernetes'],
      estimated_weeks: 12,
      study_hours: 10,
      roadmap: [{ step: 1, skill: 'Kubernetes', category: 'Cloud', estimated_hours: 20 }],
      ai_summary: 'Good foundation.',
    };
    sessionStorage.setItem('assessment', JSON.stringify(assessmentData));
    mockGetAssessment.mockResolvedValue({ success: false });

    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText('Career Dashboard')).toBeDefined();
      expect(screen.getByText(/SOC Analyst/)).toBeDefined();
    });
  });

  it('renders readiness gauge with score', async () => {
    sessionStorage.setItem('assessment', JSON.stringify({
      career_goal: 'Penetration Tester',
      career_readiness: 85,
      matched_skills: ['Nmap'],
      missing_skills: ['Metasploit'],
      estimated_weeks: 8,
      study_hours: 15,
      roadmap: [],
      ai_summary: '',
    }));
    mockGetAssessment.mockResolvedValue({ success: false });
    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText('85%')).toBeDefined();
    });
  });

  it('shows matched and missing skills', async () => {
    sessionStorage.setItem('assessment', JSON.stringify({
      career_goal: 'SOC Analyst',
      career_readiness: 50,
      matched_skills: ['SIEM', 'TCP/IP'],
      missing_skills: ['Python', 'Kubernetes'],
      estimated_weeks: 16,
      study_hours: 10,
      roadmap: [],
      ai_summary: '',
    }));
    mockGetAssessment.mockResolvedValue({ success: false });
    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText('SIEM')).toBeDefined();
      expect(screen.getByText('Python')).toBeDefined();
    });
  });

  it('renders action buttons', async () => {
    sessionStorage.setItem('assessment', JSON.stringify({
      career_goal: 'SOC Analyst',
      career_readiness: 60,
      matched_skills: [],
      missing_skills: [],
      roadmap: [],
    }));
    mockGetAssessment.mockResolvedValue({ success: false });
    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText('View Roadmap')).toBeDefined();
      expect(screen.getByText('Ask AI Mentor')).toBeDefined();
      expect(screen.getByText('Retake Assessment')).toBeDefined();
    });
  });

  it('loads assessment from backend by ID', async () => {
    sessionStorage.setItem('assessment_id', 'test-id-123');
    mockGetAssessment.mockResolvedValue({
      success: true,
      data: {
        career_goal: 'Cloud Security Engineer',
        career_readiness: 70,
        matched_skills: ['AWS'],
        missing_skills: ['Terraform'],
        estimated_weeks: 10,
        study_hours: 12,
        roadmap: [],
        ai_summary: '',
      },
    });
    render(<DashboardPage />);
    await waitFor(() => {
      expect(mockGetAssessment).toHaveBeenCalledWith('test-id-123');
      expect(screen.getByText('Cloud Security Engineer')).toBeDefined();
    });
  });
});
