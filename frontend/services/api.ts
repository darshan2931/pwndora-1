const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

const getToken = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token');
  }
  return null;
};

const getHeaders = (isFormData = false) => {
  const headers: Record<string, string> = {};
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  }
  return headers;
};

const handleResponse = async (res: Response) => {
  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    throw new Error('Unauthorized');
  }
  if (!res.ok) {
    try {
      const err = await res.json();
      throw new Error(err.detail || 'API Request Failed');
    } catch (e) {
      if (e instanceof SyntaxError) throw new Error('API Request Failed');
      throw e;
    }
  }
  return res.json();
};

export const api = {
  analyzeResume: async (formData: FormData) => {
    const res = await fetch(`${API_BASE}/career/analyze`, {
      method: 'POST',
      headers: getHeaders(true),
      body: formData,
    });
    return handleResponse(res);
  },

  saveAssessment: async (data: any) => {
    const res = await fetch(`${API_BASE}/career/save`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },

  chat: async (message: string) => {
    const res = await fetch(`${API_BASE}/mentor/chat`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ question: message, session_id: 'default' }),
    });
    return handleResponse(res);
  },

  getProfile: async () => {
    const res = await fetch(`${API_BASE}/auth/me`, {
      method: 'GET',
      headers: getHeaders(),
    });
    if (res.status === 401) return null;
    return handleResponse(res);
  },
  
  getReadiness: async () => {
    const res = await fetch(`${API_BASE}/career/readiness`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getDashboardData: async () => {
    const res = await fetch(`${API_BASE}/career/dashboard`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },
  
  getRecommendations: async () => {
    const res = await fetch(`${API_BASE}/recommendations`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  toggleRoadmapStep: async (roadmapId: string, stepIndex: number) => {
    const res = await fetch(`${API_BASE}/roadmap/${roadmapId}/step/${stepIndex}/toggle`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  analyzeResumeProfile: async (formData: FormData) => {
    const res = await fetch(`${API_BASE}/resume/profile/analyze`, {
      method: 'POST',
      headers: getHeaders(true),
      body: formData,
    });
    return handleResponse(res);
  },

  getResumeProfile: async () => {
    const res = await fetch(`${API_BASE}/resume/profile`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  analyzeGithub: async (forceRefresh = false) => {
    const params = forceRefresh ? '?force_refresh=true' : '';
    const res = await fetch(`${API_BASE}/github/analyze${params}`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getGithubProfile: async () => {
    const res = await fetch(`${API_BASE}/github/profile`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getGithubEvidence: async () => {
    const res = await fetch(`${API_BASE}/github/evidence`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  analyzeSkillEvidence: async (forceRefresh = false) => {
    const params = forceRefresh ? '?force_refresh=true' : '';
    const res = await fetch(`${API_BASE}/skills/evidence/analyze${params}`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getSkillEvidence: async () => {
    const res = await fetch(`${API_BASE}/skills/evidence`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getSkillEvidenceDetail: async (skillId: string) => {
    const res = await fetch(`${API_BASE}/skills/evidence/${encodeURIComponent(skillId)}`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getCareerRoles: async () => {
    const res = await fetch(`${API_BASE}/career/roles`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getCareerRoleDetail: async (roleId: string) => {
    const res = await fetch(`${API_BASE}/career/roles/${encodeURIComponent(roleId)}`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  selectTargetRole: async (roleId: string) => {
    const res = await fetch(`${API_BASE}/career/role/select`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ role_id: roleId }),
    });
    return handleResponse(res);
  },

  runGapAnalysis: async (roleId: string, forceRefresh = false) => {
    const res = await fetch(`${API_BASE}/career/gap-analysis`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ role_id: roleId, force_refresh: forceRefresh }),
    });
    return handleResponse(res);
  },

  getGapAnalysis: async () => {
    const res = await fetch(`${API_BASE}/career/gap-analysis`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getNextSkill: async () => {
    const res = await fetch(`${API_BASE}/career/next-skill`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  generateRoadmap: async (data: {
    role_id: string;
    assessment_id: string;
    weekly_hours?: number;
    learning_style?: string;
  }) => {
    const res = await fetch(`${API_BASE}/roadmap/generate`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },

  regenerateRoadmap: async (data: {
    role_id: string;
    assessment_id: string;
    weekly_hours?: number;
    learning_style?: string;
    preserve_completed?: boolean;
  }) => {
    const res = await fetch(`${API_BASE}/roadmap/regenerate`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },

  getCurrentRoadmap: async () => {
    const res = await fetch(`${API_BASE}/roadmap/current`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getRoadmapById: async (roadmapId: string) => {
    const res = await fetch(`${API_BASE}/roadmap/${encodeURIComponent(roadmapId)}`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  toggleRoadmapNode: async (roadmapId: string, nodeIndex: number) => {
    const res = await fetch(`${API_BASE}/roadmap/${roadmapId}/node/${nodeIndex}/toggle`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
  },

  // ─── Phase 6: Career Evidence Event Loop ────────────────────────────────────

  createCareerEvent: async (eventType: string, eventData: Record<string, any> = {}, idempotencyKey?: string) => {
    const formData = new URLSearchParams();
    formData.append('event_type', eventType);
    formData.append('event_data', JSON.stringify(eventData));
    if (idempotencyKey) {
      formData.append('idempotency_key', idempotencyKey);
    }
    const res = await fetch(`${API_BASE}/career/events`, {
      method: 'POST',
      headers: {
        ...getHeaders(),
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });
    return handleResponse(res);
  },

  processCareerEvent: async (eventId: string) => {
    const res = await fetch(`${API_BASE}/career/events/${eventId}/process`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getCareerEventStatus: async (eventId: string) => {
    const res = await fetch(`${API_BASE}/career/events/${eventId}`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getCareerTimeline: async (limit = 20) => {
    const res = await fetch(`${API_BASE}/career/timeline?limit=${limit}`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getCareerProgress: async () => {
    const res = await fetch(`${API_BASE}/career/progress`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getCareerChanges: async (limit = 50) => {
    const res = await fetch(`${API_BASE}/career/changes?limit=${limit}`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  reanalyzeGithubRepo: async (repoId: string) => {
    const res = await fetch(`${API_BASE}/github/repositories/${repoId}/reanalyze`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getRoadmapVersions: async (limit = 10) => {
    const res = await fetch(`${API_BASE}/career/versions?limit=${limit}`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  // ─── Phase 7: Enhanced AI Mentor ────────────────────────────────────────────

  generateMentorResponse: async (question: string, sessionId = 'default', mode?: string) => {
    const res = await fetch(`${API_BASE}/mentor/generate`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ question, session_id: sessionId, mode: mode || '' }),
    });
    return handleResponse(res);
  },

  getDailyBriefing: async () => {
    const res = await fetch(`${API_BASE}/mentor/daily-briefing`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getRoadmapExplanation: async () => {
    const res = await fetch(`${API_BASE}/mentor/roadmap-explanation`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getSkillExplanation: async (skillId: string) => {
    const res = await fetch(`${API_BASE}/mentor/skill-explanation`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ skill_id: skillId }),
    });
    return handleResponse(res);
  },

  getInterviewPrep: async () => {
    const res = await fetch(`${API_BASE}/mentor/interview-prep`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  // ─── Phase 8: Career Opportunity Intelligence ─────────────────────────────

  getOpportunities: async () => {
    const res = await fetch(`${API_BASE}/opportunities`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getOpportunity: async (opportunityId: string) => {
    const res = await fetch(`${API_BASE}/opportunities/${encodeURIComponent(opportunityId)}`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  matchOpportunity: async (opportunityId: string) => {
    const res = await fetch(`${API_BASE}/opportunities/${encodeURIComponent(opportunityId)}/match`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getRecommendedOpportunities: async () => {
    const res = await fetch(`${API_BASE}/opportunities/recommended/top`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getUserMatches: async () => {
    const res = await fetch(`${API_BASE}/opportunities/matches`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  prepareOpportunity: async (opportunityId: string) => {
    const res = await fetch(`${API_BASE}/opportunities/${encodeURIComponent(opportunityId)}/prepare`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  compareOpportunities: async (opportunityIds: string[]) => {
    const params = opportunityIds.join(',');
    const res = await fetch(`${API_BASE}/opportunities/compare?opportunity_ids=${encodeURIComponent(params)}`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  explainOpportunity: async (opportunityId: string) => {
    const res = await fetch(`${API_BASE}/mentor/explain-opportunity/${encodeURIComponent(opportunityId)}`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },
};

export default api;
