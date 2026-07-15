import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Suspense } from 'react';
import UploadPage from '@/app/upload/page';

const mockAnalyzeCareer = vi.fn();
const mockSaveAssessment = vi.fn();
vi.mock('@/services/api', () => ({
  analyzeCareer: (...args: unknown[]) => mockAnalyzeCareer(...args),
  saveAssessment: (...args: unknown[]) => mockSaveAssessment(...args),
}));

function renderWithSuspense(ui: React.ReactElement) {
  return render(<Suspense fallback={<div>Loading...</div>}>{ui}</Suspense>);
}

describe('UploadPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it('renders the page title', () => {
    renderWithSuspense(<UploadPage />);
    expect(screen.getByText('Career Assessment')).toBeDefined();
  });

  it('shows career select dropdown', () => {
    renderWithSuspense(<UploadPage />);
    expect(screen.getByText('Target Career')).toBeDefined();
  });

  it('shows study hours slider', () => {
    renderWithSuspense(<UploadPage />);
    expect(screen.getByText('Weekly Study Hours')).toBeDefined();
    expect(screen.getByText('10h/wk')).toBeDefined();
  });

  it('shows upload mode toggle', () => {
    renderWithSuspense(<UploadPage />);
    expect(screen.getByText('Upload Resume')).toBeDefined();
    expect(screen.getByText('Enter Skills Manually')).toBeDefined();
  });

  it('switches to manual mode', () => {
    renderWithSuspense(<UploadPage />);
    fireEvent.click(screen.getByText('Enter Skills Manually'));
    expect(screen.getByText('Your Skills (comma-separated)')).toBeDefined();
  });

  it('shows file drop zone in file mode', () => {
    renderWithSuspense(<UploadPage />);
    expect(screen.getByLabelText('Upload resume file')).toBeDefined();
    expect(screen.getByText(/Click to upload/)).toBeDefined();
  });

  it('submit button is disabled when no career selected', () => {
    renderWithSuspense(<UploadPage />);
    const submitBtn = screen.getByText('Analyze My Profile');
    expect(submitBtn.closest('button')).toHaveProperty('disabled', true);
  });

  it('submit button enables when career is selected', () => {
    renderWithSuspense(<UploadPage />);
    fireEvent.change(screen.getByDisplayValue('Select a career path...'), { target: { value: 'SOC Analyst' } });
    const submitBtn = screen.getByText('Analyze My Profile');
    expect(submitBtn.closest('button')).not.toHaveProperty('disabled', true);
  });
});
