'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { FormField } from '@/components/ui/form-field'
import { FormStatus, useFormStatus } from '@/components/ui/form-status'
import { ArrowRight } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { validateEmail } from '@/lib/validation'
import * as z from 'zod'
import { createClient } from '@/lib/supabase/client'

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
})

type LoginFormData = z.infer<typeof loginSchema>

export default function LoginPage() {
  const router = useRouter()
  const formStatus = useFormStatus()

    // OAuth login handlers
    const handleGoogleLogin = async () => {
          const supabase = createClient()
          const { error } = await supabase.auth.signInWithOAuth({
                  provider: 'google',
                  options: {
                            redirectTo: `${window.location.origin}/auth/callback`,
                  },
          })
          if (error) {
                  formStatus.setError('Google login failed', error.message)
          }
    }

    const handleGithubLogin = async () => {
          const supabase = createClient()
          const { error } = await supabase.auth.signInWithOAuth({
                  provider: 'github',
                  options: {
                            redirectTo: `${window.location.origin}/auth/callback`,
                  },
          })
          if (error) {
                  formStatus.setError('GitHub login failed', error.message)
          }
    }

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const watchedEmail = watch('email')

  const onSubmit = async (data: LoginFormData) => {
    formStatus.setSubmitting('Signing you in...')
    
    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error('Invalid credentials')
      }

      const result = await response.json()

      // Store auth token (in production, use secure httpOnly cookies)
      localStorage.setItem('authToken', result.token)

      formStatus.setSuccess(
        'Login successful!', 
        'Redirecting to your dashboard...'
      )

      // Redirect after showing success message briefly
      setTimeout(() => {
        router.push('/dashboard')
      }, 1500)
    } catch (error) {
      console.error('Login error:', error)
      formStatus.setError(
        'Login failed',
        'Please check your email and password and try again.'
      )
    }
  }

  return (
    <div className="flex min-h-screen">
      {/* Left side - Form */}
      <div className="flex w-full flex-col justify-center px-8 py-12 lg:w-1/2 lg:px-16">
        <div className="mx-auto w-full max-w-sm">
          <h1 className="text-2xl font-bold mb-2">Welcome back</h1>
          <p className="text-sm text-muted-foreground mb-8">
            Don't have an account?{' '}
            <Link href="/signup" className="text-primary hover:underline">
              Sign up for free
            </Link>
          </p>

          {/* Form Status */}
          <FormStatus 
            status={formStatus.status}
            message={formStatus.message}
            details={formStatus.details}
            className="mb-6"
            autoHideSuccess={5000}
            onStatusChange={formStatus.updateStatus}
          />

          {/* Login Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              id="email"
              label="Email"
              type="email"
              placeholder="your@email.com"
              {...register('email')}
              error={errors.email?.message}
              success={!!(watchedEmail && !errors.email && watchedEmail.includes('@'))}
              helperText="Enter your registered email address"
              onValidation={validateEmail}
              required
            />

            <FormField
              id="password"
              label="Password"
              type="password"
              placeholder="Enter your password"
              {...register('password')}
              error={errors.password?.message}
              showPasswordToggle
              required
            />

            <Button
              type="submit"
              className="w-full"
              size="lg"
              disabled={formStatus.status === 'submitting'}
            >
              {formStatus.status === 'submitting' ? (
                'Signing in...'
              ) : (
                <>
                  Sign in
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">
                  Or continue with
                </span>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-2 gap-3">
              {/* Google OAuth */}
              <Button variant="outline" onClick={handleGoogleLogin}>
                <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                  <path
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    fill="#4285F4"
                  />
                  <path
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    fill="#34A853"
                  />
                  <path
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    fill="#EA4335"
                  />
                </svg>
                Google
              </Button>
              {/* GitHub OAuth */}
              <Button variant="outline" onClick={handleGithubLogin}>
                <svg className="mr-2 h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                GitHub
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Image/Benefits */}
      <div className="hidden lg:flex lg:w-1/2 bg-primary/5 items-center justify-center p-16">
        <div className="max-w-md">
          <h2 className="text-3xl font-bold mb-6">Welcome back to Monkey Coder</h2>
          <p className="text-lg text-muted-foreground mb-8">
            Sign in to access your AI-powered development tools and continue building amazing software.
          </p>

          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-1 mt-0.5">
                <ArrowRight className="h-4 w-4 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold">Access your projects</h3>
                <p className="text-sm text-muted-foreground">
                  Continue where you left off with your saved projects and configurations
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-1 mt-0.5">
                <ArrowRight className="h-4 w-4 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold">View usage analytics</h3>
                <p className="text-sm text-muted-foreground">
                  Track your code generation usage and optimize your workflow
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-1 mt-0.5">
                <ArrowRight className="h-4 w-4 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold">Manage your subscription</h3>
                <p className="text-sm text-muted-foreground">
                  Upgrade, downgrade, or modify your plan anytime
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
