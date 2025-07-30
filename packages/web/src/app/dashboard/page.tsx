'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Zap, Clock, BarChart3, CreditCard, Settings, LogOut, ArrowUpRight } from 'lucide-react'

interface User {
  id: string
  name: string
  email: string
  plan: string
}

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [stats, setStats] = useState({
    generationsToday: 12,
    generationsMonth: 342,
    tokensUsed: 125420,
    apiCalls: 89,
  })

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('authToken')
    if (!token) {
      router.push('/login')
      return
    }

    // Mock user data (in production, fetch from API)
    setUser({
      id: '1',
      name: 'Demo User',
      email: 'demo@example.com',
      plan: 'pro'
    })
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('authToken')
    router.push('/login')
  }

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/dashboard" className="flex items-center gap-2">
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
                className="h-8 w-8"
              />
            </Link>
            <nav className="hidden md:flex items-center gap-6">
              <Link href="/dashboard" className="text-sm font-medium">
                Dashboard
              </Link>
              <Link href="/projects" className="text-sm font-medium text-muted-foreground hover:text-primary">
                Projects
              </Link>
              <Link href="/api-keys" className="text-sm font-medium text-muted-foreground hover:text-primary">
                API Keys
              </Link>
              <Link href="/docs" className="text-sm font-medium text-muted-foreground hover:text-primary">
                Documentation
              </Link>
            </nav>
          </div>

          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" className="gap-2">
              <CreditCard className="h-4 w-4" />
              {user.plan === 'pro' ? 'Pro Plan' : 'Hobby Plan'}
            </Button>
            <Button variant="ghost" size="icon" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Welcome back, {user.name}!</h1>
          <p className="text-muted-foreground mt-2">
            Here's an overview of your usage and recent activity.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <div className="rounded-lg border bg-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Generations Today
                </p>
                <p className="text-2xl font-bold mt-2">{stats.generationsToday}</p>
              </div>
              <Zap className="h-8 w-8 text-primary opacity-20" />
            </div>
          </div>

          <div className="rounded-lg border bg-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  This Month
                </p>
                <p className="text-2xl font-bold mt-2">{stats.generationsMonth}</p>
              </div>
              <BarChart3 className="h-8 w-8 text-primary opacity-20" />
            </div>
          </div>

          <div className="rounded-lg border bg-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Tokens Used
                </p>
                <p className="text-2xl font-bold mt-2">
                  {(stats.tokensUsed / 1000).toFixed(1)}k
                </p>
              </div>
              <Clock className="h-8 w-8 text-primary opacity-20" />
            </div>
          </div>

          <div className="rounded-lg border bg-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  API Calls
                </p>
                <p className="text-2xl font-bold mt-2">{stats.apiCalls}</p>
              </div>
              <Settings className="h-8 w-8 text-primary opacity-20" />
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-lg border bg-card p-6">
            <h3 className="font-semibold mb-2">New Code Generation</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Generate code using our AI-powered engine
            </p>
            <Button className="w-full" size="sm">
              <Zap className="mr-2 h-4 w-4" />
              Start Generating
            </Button>
          </div>

          <div className="rounded-lg border bg-card p-6">
            <h3 className="font-semibold mb-2">API Documentation</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Learn how to integrate our API into your workflow
            </p>
            <Button variant="outline" className="w-full" size="sm">
              View Docs
              <ArrowUpRight className="ml-2 h-4 w-4" />
            </Button>
          </div>

          <div className="rounded-lg border bg-card p-6">
            <h3 className="font-semibold mb-2">Manage Subscription</h3>
            <p className="text-sm text-muted-foreground mb-4">
              {user.plan === 'pro'
                ? 'Manage your Pro subscription and billing'
                : 'Upgrade to Pro for unlimited generations'
              }
            </p>
            <Button variant="outline" className="w-full" size="sm">
              {user.plan === 'pro' ? 'Manage Plan' : 'Upgrade to Pro'}
            </Button>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Recent Generations</h2>
          <div className="rounded-lg border">
            <div className="p-4 text-sm text-muted-foreground text-center">
              No recent generations. Start generating code to see your history here.
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
