'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { useAuth } from '@/contexts/auth-context'
import { Loader2 } from 'lucide-react'

export default function AuthCallbackPage() {
  const router = useRouter()
  const { login } = useAuth()

  useEffect(() => {
    const handleCallback = async () => {
      // Supabase exchanges the URL hash/code for a session automatically
      const { data, error } = await supabase.auth.getSession()

      if (error || !data.session) {
        console.error('OAuth callback error:', error)
        router.replace('/login?error=oauth_failed')
        return
      }

      const session = data.session
      const sbUser = session.user

      login(
        {
          id: sbUser.id,
          name:
            sbUser.user_metadata?.full_name ||
            sbUser.user_metadata?.name ||
            sbUser.email?.split('@')[0] ||
            'User',
          email: sbUser.email!,
          avatar: sbUser.user_metadata?.avatar_url,
        },
        session.access_token
      )

      router.replace('/dashboard')
    }

    handleCallback()
  }, [login, router])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-background">
      <Loader2 className="h-10 w-10 animate-spin text-primary" />
      <p className="text-muted-foreground text-sm">Completing sign-in...</p>
    </div>
  )
}
