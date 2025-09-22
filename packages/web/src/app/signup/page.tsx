'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { FormField } from '@/components/ui/form-field'
import { FormStatus, useFormStatus } from '@/components/ui/form-status'
import { PasswordStrengthIndicator } from '@/components/ui/password-strength'
import { Label } from '@/components/ui/label'
import { ArrowRight } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { 
  validateEmail, 
  validateUsername, 
  validatePassword, 
  validateConfirmPassword,
  validateName,
  checkEmailAvailability,
  checkUsernameAvailability
} from '@/lib/validation'
import * as z from 'zod'

const signupSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters').max(20, 'Username must be less than 20 characters').regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores'),
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
})

type SignupFormData = z.infer<typeof signupSchema>

export default function SignupPage() {
  const router = useRouter()
  const formStatus = useFormStatus()
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
  })

  const watchedPassword = watch('password')
  const watchedEmail = watch('email')
  const watchedUsername = watch('username')

  const onSubmit = async (_data: SignupFormData) => {
    formStatus.setSubmitting('Creating your account...')
    
    try {
      // TODO: Signup endpoint not yet implemented in backend
      // For now, show a message that signup is coming soon
      
      // Simulate API delay for realistic UX
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      formStatus.setSuccess(
        'Account created successfully!',
        'Please check your email to verify your account.'
      )
      
      // For demo purposes, redirect to login after success message
      setTimeout(() => {
        router.push('/login')
      }, 3000)
      
    } catch (error) {
      console.error('Signup error:', error)
      formStatus.setError(
        'Signup failed',
        'Unable to create account. Please try again.'
      )
    }
  }

  return (
    <div className="flex min-h-screen">
      {/* Left side - Form */}
      <div className="flex w-full flex-col justify-center px-8 py-12 lg:w-1/2 lg:px-16">
        <div className="mx-auto w-full max-w-sm">
          <h1 className="text-2xl font-bold mb-2">Create your account</h1>
          <p className="text-sm text-muted-foreground mb-8">
            Already have an account?{' '}
            <Link href="/login" className="text-primary hover:underline">
              Sign in
            </Link>
          </p>

          {/* Plan Selection */}
          <div className="mb-6">
            <Label className="text-base font-semibold mb-3 block">Choose your plan</Label>
            <div className="space-y-3">
              <div
                className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                  selectedPlan === 'hobby'
                    ? 'border-primary bg-primary/5'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedPlan('hobby')}
              >
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold">Hobby</h3>
                    <p className="text-sm text-muted-foreground">Perfect for side projects</p>
                  </div>
                  <span className="font-bold">$0/mo</span>
                </div>
              </div>

              <div
                className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                  selectedPlan === 'pro'
                    ? 'border-primary bg-primary/5'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedPlan('pro')}
              >
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold">Pro</h3>
                    <p className="text-sm text-muted-foreground">For professional developers</p>
                  </div>
                  <span className="font-bold">$29/mo</span>
                </div>
                <p className="text-xs text-primary mt-2">Most popular</p>
              </div>
            </div>
          </div>

          {/* Form Status */}
          <FormStatus 
            status={formStatus.status}
            message={formStatus.message}
            details={formStatus.details}
            className="mb-6"
            autoHideSuccess={8000}
            onStatusChange={formStatus.updateStatus}
          />

          {/* Signup Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              id="username"
              label="Username"
              placeholder="garyocean"
              {...register('username')}
              error={errors.username?.message}
              success={!!(watchedUsername && !errors.username && watchedUsername.length >= 3)}
              helperText="Choose a unique username (3-20 characters)"
              onValidation={async (value) => {
                const basicError = validateUsername(value)
                if (basicError) return basicError
                return await checkUsernameAvailability(value)
              }}
              required
            />

            <FormField
              id="name"
              label="Full Name"
              placeholder="John Doe"
              {...register('name')}
              error={errors.name?.message}
              success={!!(watchedEmail && !errors.name)}
              helperText="Your real name as you'd like it displayed"
              onValidation={(value) => validateName(value, "Full name")}
              required
            />

            <FormField
              id="email"
              label="Email"
              type="email"
              placeholder="you@example.com"
              {...register('email')}
              error={errors.email?.message}
              success={!!(watchedEmail && !errors.email && watchedEmail.includes('@'))}
              helperText="We'll send you a verification email"
              onValidation={async (value) => {
                const basicError = validateEmail(value)
                if (basicError) return basicError
                return await checkEmailAvailability(value)
              }}
              required
            />

            <div className="space-y-4">
              <FormField
                id="password"
                label="Password"
                type="password"
                placeholder="Create a strong password"
                {...register('password')}
                error={errors.password?.message}
                showPasswordToggle
                helperText="Must be at least 8 characters with mixed case, numbers, and symbols"
                onValidation={validatePassword}
                required
              />
              
              {/* Password Strength Indicator */}
              {watchedPassword && (
                <PasswordStrengthIndicator 
                  password={watchedPassword}
                  className="mt-3"
                />
              )}
            </div>

            <FormField
              id="confirmPassword"
              label="Confirm Password"
              type="password"
              placeholder="Confirm your password"
              {...register('confirmPassword')}
              error={errors.confirmPassword?.message}
              success={!!(watchedPassword && watch('confirmPassword') && watchedPassword === watch('confirmPassword'))}
              showPasswordToggle
              onValidation={(value) => validateConfirmPassword(watchedPassword || '', value)}
              required
            />

            <Button
              type="submit"
              className="w-full"
              size="lg"
              disabled={formStatus.status === 'submitting' || !selectedPlan}
            >
              {formStatus.status === 'submitting' ? (
                'Creating account...'
              ) : (
                <>
                  {selectedPlan === 'pro' ? 'Continue to payment' : 'Create free account'}
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>

            <p className="text-xs text-center text-muted-foreground mt-4">
              By creating an account, you agree to our{' '}
              <Link href="/terms" className="underline">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link href="/privacy" className="underline">
                Privacy Policy
              </Link>
            </p>
          </form>
        </div>
      </div>

      {/* Right side - Benefits */}
      <div className="hidden lg:flex lg:w-1/2 bg-primary/5 items-center justify-center p-16">
        <div className="max-w-md">
          <h2 className="text-3xl font-bold mb-6">Start building with AI today</h2>
          <ul className="space-y-4">
            <li className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-1 mt-0.5">
                <ArrowRight className="h-4 w-4 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold">Instant code generation</h3>
                <p className="text-sm text-muted-foreground">
                  Generate production-ready code in seconds, not hours
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-1 mt-0.5">
                <ArrowRight className="h-4 w-4 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold">Support for 358+ languages</h3>
                <p className="text-sm text-muted-foreground">
                  From Python to Rust, we've got you covered
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <div className="rounded-full bg-primary/10 p-1 mt-0.5">
                <ArrowRight className="h-4 w-4 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold">Built by developers, for developers</h3>
                <p className="text-sm text-muted-foreground">
                  We understand your workflow and optimize for it
                </p>
              </div>
            </li>
          </ul>

          {selectedPlan === 'pro' && (
            <div className="mt-8 p-4 bg-primary/10 rounded-lg">
              <h4 className="font-semibold mb-2">Pro Plan Benefits:</h4>
              <ul className="text-sm space-y-1">
                <li>• Unlimited code generations</li>
                <li>• Access to all AI models</li>
                <li>• Priority support</li>
                <li>• Team collaboration</li>
                <li>• API access</li>
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
