'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ArrowRight, Loader2 } from 'lucide-react'
import Image from 'next/image'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
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
  const [isLoading, setIsLoading] = useState(false)
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
  })

  const onSubmit = async (data: SignupFormData) => {
    setIsLoading(true)
    try {
      // Create user account
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: data.username,
          name: data.name,
          email: data.email,
          password: data.password,
          plan: selectedPlan || 'hobby',
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to create account')
      }

      const result = await response.json()

      // If Pro plan selected, redirect to Stripe checkout
      if (selectedPlan === 'pro') {
        window.location.href = result.checkoutUrl
      } else {
        // For free plan, redirect to dashboard
        router.push('/dashboard')
      }
    } catch (error) {
      console.error('Signup error:', error)
      alert('Failed to create account. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      {/* Left side - Form */}
      <div className="flex w-full flex-col justify-center px-8 py-12 lg:w-1/2 lg:px-16">
        <div className="mx-auto w-full max-w-sm">
          <Link href="/" className="flex items-center gap-2 mb-8">
            <Image
              src="/favicon.ico"
              alt="Favicon Logo"
              width={24}
              height={24}
              className="h-6 w-6"
            />
            <Image
              src="/splash.png"
              alt="Splash Logo"
              width={120}
              height={32}
              className="h-8 w-auto object-contain"
              priority
            />
          </Link>

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

          {/* Signup Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                placeholder="garyocean"
                {...register('username')}
                className="mt-1"
              />
              {errors.username && (
                <p className="text-sm text-destructive mt-1">{errors.username.message}</p>
              )}
            </div>

            <div>
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                placeholder="John Doe"
                {...register('name')}
                className="mt-1"
              />
              {errors.name && (
                <p className="text-sm text-destructive mt-1">{errors.name.message}</p>
              )}
            </div>

            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                {...register('email')}
                className="mt-1"
              />
              {errors.email && (
                <p className="text-sm text-destructive mt-1">{errors.email.message}</p>
              )}
            </div>

            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                {...register('password')}
                className="mt-1"
              />
              {errors.password && (
                <p className="text-sm text-destructive mt-1">{errors.password.message}</p>
              )}
            </div>

            <div>
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="••••••••"
                {...register('confirmPassword')}
                className="mt-1"
              />
              {errors.confirmPassword && (
                <p className="text-sm text-destructive mt-1">{errors.confirmPassword.message}</p>
              )}
            </div>

            <Button
              type="submit"
              className="w-full"
              size="lg"
              disabled={isLoading || !selectedPlan}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating account...
                </>
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
