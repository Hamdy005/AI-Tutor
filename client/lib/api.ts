// API Configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

// Types
export interface User {
  id: string
  name: string
  email: string
  avatar?: string
}

export interface Material {
  id: string
  title: string
  source_type: 'pdf' | 'url'
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

// API Helper
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
    throw new Error(error.message || `HTTP error! status: ${response.status}`)
  }

  return response.json()
}

// Auth API
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

// Materials API
export const materialsAPI = {
  list: () => fetchAPI<Material[]>('/api/materials'),

  uploadPDF: async (file: File) => {
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
      throw new Error('Failed to upload PDF')
    }

    return response.json() as Promise<Material>
  },

  scrapeURL: (url: string, source_type: 'url') =>
    fetchAPI<Material>('/api/materials/scrape-url', {
      method: 'POST',
      body: JSON.stringify({ url, source_type }),
    }),

  summarize: (material_id: string) =>
    fetchAPI<{ summary: string }>('/api/materials/summarize', {
      method: 'POST',
      body: JSON.stringify({ material_id }),
    }),
}

// Tutor API
export const tutorAPI = {
  ask: (material_id: string, question: string, chat_history: ChatMessage[]) =>
    fetchAPI<{ response: string }>('/api/tutor/ask', {
      method: 'POST',
      body: JSON.stringify({ material_id, question, chat_history }),
    }),
}

// Quiz API
export const quizAPI = {
  generate: (
    material_id: string,
    source_type: string,
    difficulty: 'easy' | 'medium' | 'hard',
    mcq_count: number,
    tf_count: number
  ) =>
    fetchAPI<QuizQuestion[]>('/api/quiz/generate', {
      method: 'POST',
      body: JSON.stringify({ material_id, source_type, difficulty, mcq_count, tf_count }),
    }),
}
