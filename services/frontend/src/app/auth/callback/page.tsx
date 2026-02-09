'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'

/**
 * Auth callback page for Supabase OAuth
 * Handles the redirect after Google/GitHub OAuth login
 * Client-side component to work with static export
 */
export default function AuthCallbackPage() {
  const router = useRouter()

  useEffect(() => {
    const handleCallback = async () => {
      const supabase = createClient()
      const { searchParams } = new URL(window.location.href)
      const code = searchParams.get('code')

      if (code) {
        await supabase.auth.exchangeCodeForSession(code)
      }

      // Redirect to dashboard after successful authentication
      router.push('/dashboard')
    }

    handleCallback()
  }, [router])

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-2">Authenticating...</h1>
        <p className="text-muted-foreground">Please wait while we complete your login.</p>
      </div>
    </div>
  )
}

