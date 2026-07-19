const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

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
    throw new Error('API Request Failed');
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
  
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
  }
};

export default api;
