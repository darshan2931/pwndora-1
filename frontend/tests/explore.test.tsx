import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import ExplorePage from '@/app/explore/page';

const mockGetCareers = vi.fn();
vi.mock('@/services/api', () => ({
  getCareers: (...args: unknown[]) => mockGetCareers(...args),
}));

describe('ExplorePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the page title', async () => {
    mockGetCareers.mockResolvedValue({ success: true, data: [] });
    render(<ExplorePage />);
    expect(screen.getByText('Explore Cybersecurity Careers')).toBeDefined();
  });

  it('shows loading skeleton while fetching', () => {
    mockGetCareers.mockReturnValue(new Promise(() => {}));
    render(<ExplorePage />);
    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('renders career cards from API', async () => {
    mockGetCareers.mockResolvedValue({
      success: true,
      data: [
        { id: '1', title: 'SOC Analyst', description: 'Monitor security incidents.' },
        { id: '2', title: 'Penetration Tester', description: 'Find vulnerabilities.' },
      ],
    });
    render(<ExplorePage />);
    await waitFor(() => {
      expect(screen.getByText('SOC Analyst')).toBeDefined();
      expect(screen.getByText('Penetration Tester')).toBeDefined();
    });
  });

  it('falls back to constants when API fails', async () => {
    mockGetCareers.mockRejectedValue(new Error('Network error'));
    render(<ExplorePage />);
    await waitFor(() => {
      expect(screen.getByText('SOC Analyst')).toBeDefined();
      expect(screen.getByText('Penetration Tester')).toBeDefined();
    });
  });

  it('displays skill filter buttons', async () => {
    mockGetCareers.mockResolvedValue({ success: true, data: [] });
    render(<ExplorePage />);
    expect(screen.getByText('All Careers')).toBeDefined();
    expect(screen.getByText('Filter by Skill')).toBeDefined();
  });

  it('shows start assessment link for each career', async () => {
    mockGetCareers.mockResolvedValue({
      success: true,
      data: [{ id: '1', title: 'SOC Analyst', description: 'Test' }],
    });
    render(<ExplorePage />);
    await waitFor(() => {
      const links = screen.getAllByText('Start Assessment →');
      expect(links.length).toBeGreaterThanOrEqual(1);
    });
  });
});
