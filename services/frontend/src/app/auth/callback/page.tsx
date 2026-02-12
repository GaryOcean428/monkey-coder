'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { exchangeSupabaseToken } from '@/lib/auth'

/**
 * Auth callback page for Supabase OAuth
 * Handles the redirect after Google/GitHub OAuth login
 * Client-side component to work with static export
 */
export default function AuthCallbackPage() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const { searchParams } = new URL(window.location.href)
        const code = searchParams.get('code')

        if (!code) {
          // No code means authentication failed or was cancelled
          router.push('/login?error=no_code')
          return
        }

        const supabase = createClient()
        const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(code)

        if (exchangeError) {
          console.error('Auth exchange error:', exchangeError)
          setError(exchangeError.message)
          setTimeout(() => {
            router.push(`/login?error=${encodeURIComponent(exchangeError.message)}`)
          }, 2000)
          return
        }

        // Bridge Supabase session to backend JWT
        const { data: { session } } = await supabase.auth.getSession()
        if (session?.access_token) {
          try {
            await exchangeSupabaseToken(session.access_token)
          } catch (bridgeErr) {
            // Log but don't block — user has a valid Supabase session
            console.warn('Backend token exchange failed, continuing with Supabase session:', bridgeErr)
          }
        }

        // Success! Redirect to dashboard
        router.push('/dashboard')
      } catch (err) {
        console.error('Unexpected error during auth callback:', err)
        setError('An unexpected error occurred during authentication')
        setTimeout(() => {
          router.push('/login?error=unexpected')
        }, 2000)
      }
    }

    handleCallback()
  }, [router])

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-2 text-red-600">Authentication Failed</h1>
          <p className="text-muted-foreground mb-4">{error}</p>
          <p className="text-sm text-muted-foreground">Redirecting to login page...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-2">Authenticating...</h1>
        <p className="text-muted-foreground">Please wait while we complete your login.</p>
      </div>
    </div>
  )
}

