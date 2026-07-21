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

  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
  }
};

export default api;
