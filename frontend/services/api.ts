import {
  CareerAnalysisResponse,
  CareersResponse,
  ProjectsResponse,
  SkillsResponse,
  MentorChatResponse,
  CertificationsResponse,
} from '@/types';

const API_ORIGIN = process.env.NEXT_PUBLIC_API_URL || '';
const API_PREFIX = '/api/v1';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers = { ...options?.headers } as Record<string, string>;
  
  // Inject JWT Token if available
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }
  const url = API_ORIGIN ? `${API_ORIGIN}${API_PREFIX}${path}` : `${API_PREFIX}${path}`;
  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function analyzeCareer(formData: FormData): Promise<CareerAnalysisResponse> {
  return request<CareerAnalysisResponse>('/career/analyze', {
    method: 'POST',
    body: formData,
  });
}

export async function saveAssessment(data: {
  career_goal: string;
  matched_skills: string[];
  missing_skills: string[];
  readiness_score: number;
  roadmap: Array<Record<string, unknown>>;
  estimated_weeks: number;
  ai_summary: string;
  study_hours: number;
  projects: Array<Record<string, unknown>>;
}): Promise<{ success: boolean; data?: { assessment_id: string } }> {
  return request('/career/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}

export async function getAssessment(assessmentId: string): Promise<{ success: boolean; data: Record<string, unknown> }> {
  return request(`/assessments/${encodeURIComponent(assessmentId)}`);
}

export async function getCareers(): Promise<CareersResponse> {
  return request<CareersResponse>('/careers');
}

export async function getProjects(skill?: string): Promise<ProjectsResponse> {
  const params = skill ? `?skill=${encodeURIComponent(skill)}` : '';
  return request<ProjectsResponse>(`/projects${params}`);
}

export async function getProjectsBySkill(skillName: string): Promise<ProjectsResponse> {
  return request<ProjectsResponse>(`/projects/${encodeURIComponent(skillName)}`);
}

export async function getSkills(): Promise<SkillsResponse> {
  return request<SkillsResponse>('/knowledge/skills');
}

export async function getCertifications(roleName: string): Promise<CertificationsResponse> {
  return request<CertificationsResponse>(`/certifications/${encodeURIComponent(roleName)}`);
}

export async function mentorChat(question: string, assessmentId?: string): Promise<MentorChatResponse> {
  return request<MentorChatResponse>('/mentor/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, assessment_id: assessmentId || '' }),
  });
}

export async function clearMentorSession(sessionId: string): Promise<{ success: boolean }> {
  return request(`/mentor/session/${encodeURIComponent(sessionId)}`, {
    method: 'DELETE',
  });
}

export async function explainCareer(data: {
  career_goal: string;
  user_skills: string[];
}): Promise<{ success: boolean; data: { explanation: string; confidence: number } }> {
  return request('/career/explain', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}

export async function getSkillResources(skillName: string): Promise<{ success: boolean; data: Array<{ name: string; url: string; type: string }> }> {
  return request(`/resources/${encodeURIComponent(skillName)}`);
}

export async function getLearningPath(career: string): Promise<{ success: boolean; data: { career: string; sequence: string[]; projects: string[]; certifications: string[]; estimated_duration: number } }> {
  return request(`/learning-paths/${encodeURIComponent(career)}`);
}

// AUTH API

export async function login(data: Record<string, string>): Promise<{ access_token: string; token_type: string }> {
  const formBody = Object.keys(data)
    .map((key) => encodeURIComponent(key) + '=' + encodeURIComponent(data[key]))
    .join('&');
    
  return request<{ access_token: string; token_type: string }>('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formBody,
  });
}

export async function register(data: Record<string, string>): Promise<{ success: boolean; data: { id: string; email: string; name: string } }> {
  return request('/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}

export async function getCurrentUser(): Promise<{ success: boolean; data: { id: string; email: string; name: string } }> {
  return request('/auth/me');
}
