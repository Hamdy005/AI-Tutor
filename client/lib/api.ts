export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || ''

export interface User {
  id: string
  name: string
  email: string
  avatar?: string
}

export interface Material {
  id: string
  title: string
  source_type: 'pdf' | 'url' | 'topic'
  topic?: string
  status: 'pending' | 'processing' | 'ready' | 'error' | 'failed'
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export interface QuizQuestion {
  id: string
  type: 'mcq' | 'true_false'
  question: string
  options?: string[]
  correct_answer: string
}

export interface QuizResult {
  total: number
  correct: number
  incorrect: number
  score: number
  answers: {
    question_id: string
    user_answer: string
    correct_answer: string
    is_correct: boolean
  }[]
}

export interface ChatSession {
  id: string
  title: string
  material_id: string
  user_id: string
  created_at: string
  updated_at: string
}

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
  const userStr = typeof window !== 'undefined' ? localStorage.getItem('auth_user') : null
  let userId = ''
  try {
    if (userStr) userId = JSON.parse(userStr).id || ''
  } catch {}

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...(userId && { 'X-User-Id': userId }),
    ...options.headers,
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'An error occurred' }))
    throw new Error(error.message || error.detail || `HTTP error! status: ${response.status}`)
  }

  return response.json()
}

export const authAPI = {
  login: (email: string, password: string) =>
    fetchAPI<{ token: string; user: User }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  signup: (name: string, email: string, password: string) =>
    fetchAPI<{ token: string; user: User }>('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    }),

  googleAuth: (token: string) =>
    fetchAPI<{ token: string; user: User }>('/api/auth/google', {
      method: 'POST',
      body: JSON.stringify({ token }),
    }),
}

export const materialsAPI = {
  list: () => fetchAPI<Material[]>('/api/materials'),

  uploadPDF: async (file: File): Promise<{ material_id: string; title: string; chunks_count: number }> => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
    const userStr = typeof window !== 'undefined' ? localStorage.getItem('auth_user') : null
    let userId = ''
    try {
      if (userStr) userId = JSON.parse(userStr).id || ''
    } catch {}
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE_URL}/api/materials/upload-pdf`, {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
        ...(userId && { 'X-User-Id': userId }),
      },
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Failed to upload PDF' }))
      throw new Error(error.message || error.detail || 'Failed to upload PDF')
    }

    return response.json()
  },

  scrapeURL: (url: string) =>
    fetchAPI<{ material_id: string; title: string; chunks_count: number }>('/api/materials/scrape-url', {
      method: 'POST',
      body: JSON.stringify({ url }),
    }),

  addTopic: (topic: string) =>
    fetchAPI<{ material_id: string; title: string }>('/api/materials/topic', {
      method: 'POST',
      body: JSON.stringify({ topic }),
    }),

  search: (q: string) =>
    fetchAPI<{ results: string[] }>('/api/materials/search', {
      method: 'POST',
      body: JSON.stringify({ q }),
    }),

  summarize: (material_id: string) =>
    fetchAPI<{ summary: string; time_taken: number }>('/api/materials/summarize', {
      method: 'POST',
      body: JSON.stringify({ material_id }),
    }),

  get: (material_id: string) =>
    fetchAPI<Material>(`/api/materials/${material_id}`),

  getSummary: (material_id: string) =>
    fetchAPI<{ summary: string; time_taken: number }>(`/api/materials/${material_id}/summary`),

  delete: (material_id: string) =>
    fetchAPI<{ status: string }>(`/api/materials/${material_id}`, { method: 'DELETE' }),

  rename: (material_id: string, title: string) =>
    fetchAPI<{ status: string }>(`/api/materials/${material_id}`, {
      method: 'PATCH',
      body: JSON.stringify({ title }),
    }),

  bulkDelete: (material_ids: string[]) =>
    fetchAPI<{ status: string }>('/api/materials/bulk-delete', {
      method: 'POST',
      body: JSON.stringify({ material_ids }),
    }),
}

export const tutorAPI = {
  ask: (query: string, source_type: string, material_id?: string, session_id?: string) =>
    fetchAPI<{ answer: string; source: string; time_taken: number; memory_id: string }>('/api/tutor/ask', {
      method: 'POST',
      body: JSON.stringify({ query, source_type, material_id, session_id }),
    }),

  // Session management
  listSessions: (material_id: string) =>
    fetchAPI<ChatSession[]>(`/api/tutor/sessions?material_id=${material_id}`),

  createSession: (material_id: string, title?: string) =>
    fetchAPI<ChatSession>('/api/tutor/sessions', {
      method: 'POST',
      body: JSON.stringify({ material_id, title }),
    }),

  deleteSession: (session_id: string) =>
    fetchAPI<{ status: string }>(`/api/tutor/sessions/${session_id}`, { method: 'DELETE' }),

  renameSession: (session_id: string, title: string) =>
    fetchAPI<{ status: string }>(`/api/tutor/sessions/${session_id}`, {
      method: 'PATCH',
      body: JSON.stringify({ title }),
    }),

  extractTitle: (session_id: string, query: string) =>
    fetchAPI<{ status: string; title: string }>(`/api/tutor/sessions/${session_id}/extract-title`, {
      method: 'POST',
      body: JSON.stringify({ query }),
    }),

  getSessionMessages: (session_id: string) =>
    fetchAPI<{ id: string; role: string; content: string; created_at: string }[]>(
      `/api/tutor/sessions/${session_id}/messages`
    ),

  // Legacy save/load
  saveChat: (material_id: string, messages: ChatMessage[]) =>
    fetchAPI<{ status: string }>('/api/tutor/chat/save', {
      method: 'POST',
      body: JSON.stringify({ material_id, messages }),
    }),

  loadChat: (material_id: string) =>
    fetchAPI<{ messages: ChatMessage[] }>(`/api/tutor/chat/${material_id}`),
}

export const quizAPI = {
  generate: (
    difficulty: string,
    mcq_count: number,
    tf_count: number,
    source_type: string,
    material_id?: string,
    topic?: string,
  ) =>
    fetchAPI<{ quiz: Record<string, unknown>; quiz_id: string }>('/api/quiz/generate', {
      method: 'POST',
      body: JSON.stringify({ difficulty, mcq_count, tf_count, source_type, material_id, topic }),
    }),

  list: (material_id?: string) => {
    const params = material_id ? `?material_id=${material_id}` : ''
    return fetchAPI<any[]>(`/api/quiz/list${params}`)
  },

  saveResult: (quiz_id: string, result_data: Record<string, unknown>) =>
    fetchAPI<{ status: string }>('/api/quiz/save-result', {
      method: 'POST',
      body: JSON.stringify({ quiz_id, result_data }),
    }),

  getResults: (quiz_id: string) =>
    fetchAPI<any[]>(`/api/quiz/results/${quiz_id}`),
}


