import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import RoadmapPage from '@/app/roadmap/page';

const mockGetAssessment = vi.fn();
vi.mock('@/services/api', () => ({
  getAssessment: (...args: unknown[]) => mockGetAssessment(...args),
}));

describe('RoadmapPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
    mockGetAssessment.mockRejectedValue(new Error('Not found'));
  });

  it('shows no roadmap state when no data', async () => {
    render(<RoadmapPage />);
    await waitFor(() => {
      expect(screen.getByText('No Roadmap Available')).toBeDefined();
    });
  });

  it('renders roadmap from sessionStorage', async () => {
    sessionStorage.setItem('assessment', JSON.stringify({
      career_goal: 'SOC Analyst',
      career_readiness: 70,
      matched_skills: [],
      missing_skills: ['SIEM', 'Python'],
      estimated_weeks: 10,
      study_hours: 10,
      roadmap: [
        { step: 1, skill: 'SIEM', category: 'Security Tools', estimated_hours: 20, prerequisites: [] },
        { step: 2, skill: 'Python', category: 'Programming', estimated_hours: 40, prerequisites: ['SIEM'] },
      ],
      recommended_projects: [{ title: 'Lab Setup', difficulty: 'easy', estimated_hours: 10, skills: ['SIEM'] }],
    }));

    render(<RoadmapPage />);
    await waitFor(() => {
      expect(screen.getByText('Learning Roadmap')).toBeDefined();
    });
    expect(screen.getByText('SOC Analyst')).toBeDefined();
    expect(screen.getByText('SIEM')).toBeDefined();
    expect(screen.getByText('Python')).toBeDefined();
  });

  it('shows progress bar', async () => {
    sessionStorage.setItem('assessment', JSON.stringify({
      career_goal: 'SOC Analyst',
      roadmap: [
        { step: 1, skill: 'Skill A', estimated_hours: 10 },
        { step: 2, skill: 'Skill B', estimated_hours: 10 },
      ],
    }));

    render(<RoadmapPage />);
    await waitFor(() => {
      expect(screen.getByText('Overall Progress')).toBeDefined();
    });
    expect(screen.getByText(/0\/2 steps/)).toBeDefined();
  });

  it('shows recommended projects', async () => {
    sessionStorage.setItem('assessment', JSON.stringify({
      career_goal: 'SOC Analyst',
      roadmap: [],
      recommended_projects: [
        { title: 'Home Lab', difficulty: 'beginner', estimated_hours: 15, skills: ['Linux'] },
      ],
    }));

    render(<RoadmapPage />);
    await waitFor(() => {
      expect(screen.getByText('Recommended Projects')).toBeDefined();
    });
    expect(screen.getByText('Home Lab')).toBeDefined();
  });

  it('loads assessment from backend by ID', async () => {
    sessionStorage.setItem('assessment_id', 'roadmap-123');
    mockGetAssessment.mockResolvedValue({
      success: true,
      data: {
        career_goal: 'Penetration Tester',
        roadmap: [
          { step: 1, skill: 'Nmap', estimated_hours: 10 },
        ],
      },
    });

    render(<RoadmapPage />);
    await waitFor(() => {
      expect(mockGetAssessment).toHaveBeenCalledWith('roadmap-123');
      expect(screen.getByText('Nmap')).toBeDefined();
    });
  });
});
