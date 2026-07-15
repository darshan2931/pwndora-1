import {
  Assessment,
  Career,
  Project,
  Skill,
  CareerAnalysisResponse,
  CareersResponse,
  ProjectsResponse,
  SkillsResponse,
  MentorChatResponse,
  CertificationsResponse,
} from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      ...options?.headers,
    },
  });
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

export async function mentorChat(question: string, sessionId?: string): Promise<MentorChatResponse> {
  return request<MentorChatResponse>('/mentor/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, session_id: sessionId }),
  });
}

export async function explainCareer(data: {
  career_goal: string;
  matched_skills: string[];
  missing_skills: string[];
  readiness_score: number;
}): Promise<{ success: boolean; explanation: string }> {
  return request('/career/explain', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}
