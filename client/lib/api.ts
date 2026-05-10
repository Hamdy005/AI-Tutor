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
  status: 'processing' | 'ready' | 'error'
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

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
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
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE_URL}/api/materials/upload-pdf`, {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
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

  summarize: (material_id: string) =>
    fetchAPI<{ summary: string; time_taken: number }>('/api/materials/summarize', {
      method: 'POST',
      body: JSON.stringify({ material_id }),
    }),

  getSummary: (material_id: string) =>
    fetchAPI<{ summary: string; time_taken: number }>(`/api/materials/${material_id}/summary`),
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
}

export const tutorAPI = {
  ask: (query: string, source_type: string, material_id?: string, memory_id?: string) =>
    fetchAPI<{ answer: string; source: string; time_taken: number; memory_id: string }>('/api/tutor/ask', {
      method: 'POST',
      body: JSON.stringify({ query, source_type, material_id, memory_id }),
    }),
}


