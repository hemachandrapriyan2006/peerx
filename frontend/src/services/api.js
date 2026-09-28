import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Attach auth token if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('peerx_token') || localStorage.getItem('sb-token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authAPI = {
  getProfile: () => api.get('/api/auth/me'),
  updateProfile: (data) => api.put('/api/auth/me', data)
}

export const sessionAPI = {
  startSession: (data) => api.post('/api/sessions/start', data),
  getSessions: () => api.get('/api/sessions/'),
  getSession: (id) => api.get(`/api/sessions/${id}`),
  submitAnswer: (sessionId, data) => api.post(`/api/sessions/${sessionId}/answer`, data),
  getAgentResponse: (sessionId, agentType, prompt) => 
    api.post(`/api/sessions/${sessionId}/agent/${agentType}`, { prompt }),
  generateChallenge: (sessionId) => api.post(`/api/sessions/${sessionId}/challenge`)
}

export const learningAPI = {
  getDashboard: () => api.get('/api/learning/dashboard'),
  getKnowledgeGaps: () => api.get('/api/learning/knowledge-gaps'),
  getRecommendations: () => api.get('/api/learning/recommendations')
}

export const progressAPI = {
  getHistory: () => api.get('/api/progress/history'),
  getTopicMastery: () => api.get('/api/progress/topics')
}

export default api
