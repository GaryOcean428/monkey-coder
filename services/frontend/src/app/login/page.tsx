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

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
})

type LoginFormData = z.infer<typeof loginSchema>

export default function LoginPage() {
  const router = useRouter()
  const formStatus = useFormStatus()

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
