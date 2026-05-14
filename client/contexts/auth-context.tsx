'use client'

import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { supabase } from '@/lib/supabase'
import { authAPI } from '@/lib/api'

export interface UserData {
  id: string
  name: string
  email: string
  avatar?: string
  usage?: {
    used: number
    limit: number
    remaining: number
  }
}

interface AuthContextType {
  user: UserData | null
  token: string | null
  login: (user: UserData, token: string) => void
  logout: () => void
  updateUser: (data: Partial<UserData>) => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserData | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token')
    const storedUser = localStorage.getItem('auth_user')
    if (storedToken && storedUser) {
      try {
        setToken(storedToken)
        setUser(JSON.parse(storedUser))
      } catch {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_user')
      }
    }
    setIsLoading(false)
  }, [])

  useEffect(() => {
    let isActive = true
    const syncSupabaseSession = async () => {
      try {
        const { data } = await supabase.auth.getSession()
        if (!isActive) return
        const session = data.session
        if (!session) return
        const sbUser = session.user
        const authToken = session.access_token
        setToken(authToken)
        localStorage.setItem('auth_token', authToken)
        
        // Fetch full profile from our backend (includes custom name, avatar, and usage)
        try {
          const res = await authAPI.getProfile()
          if (res.user && isActive) {
            setUser(res.user)
            localStorage.setItem('auth_user', JSON.stringify(res.user))
          }
        } catch (err) {
          // If profile fetch fails, fallback to metadata as a temporary measure
          const updatedUser: UserData = {
            id: sbUser.id,
            name:
              sbUser.user_metadata?.full_name ||
              sbUser.user_metadata?.name ||
              sbUser.email?.split('@')[0] ||
              'User',
            email: sbUser.email || '',
            avatar: sbUser.user_metadata?.avatar_url,
          }
          if (isActive) {
            setUser(updatedUser)
            localStorage.setItem('auth_user', JSON.stringify(updatedUser))
          }
        }
      } catch {
        // supabase not available — nothing to sync
      }
    }

    syncSupabaseSession()

    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!session) return
      const sbUser = session.user
      const authToken = session.access_token
      setToken(authToken)
      localStorage.setItem('auth_token', authToken)

      // Fetch full profile from our backend on auth change
      authAPI.getProfile().then(res => {
        if (res.user) {
          setUser(res.user)
          localStorage.setItem('auth_user', JSON.stringify(res.user))
        }
      }).catch(() => {
        const updatedUser: UserData = {
          id: sbUser.id,
          name:
            sbUser.user_metadata?.full_name ||
            sbUser.user_metadata?.name ||
            sbUser.email?.split('@')[0] ||
            'User',
          email: sbUser.email || '',
          avatar: sbUser.user_metadata?.avatar_url,
        }
        setUser(updatedUser)
        localStorage.setItem('auth_user', JSON.stringify(updatedUser))
      })
    })

    return () => {
      isActive = false
      listener?.subscription.unsubscribe()
    }
  }, [])

  const login = (userData: UserData, authToken: string) => {
    setUser(userData)
    setToken(authToken)
    localStorage.setItem('auth_token', authToken)
    localStorage.setItem('auth_user', JSON.stringify(userData))
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
    localStorage.removeItem('cached_materials')
  }

  const updateUser = (data: Partial<UserData>) => {
    if (!user) return
    const updated = { ...user, ...data }
    setUser(updated)
    localStorage.setItem('auth_user', JSON.stringify(updated))
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, updateUser, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
