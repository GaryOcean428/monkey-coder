"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import {
  BarChart3,
  Activity,
  CreditCard,
  Plus,
  Copy,
  Eye,
  EyeOff,
  Trash2,
  RefreshCw,
  Code2,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

// Mock data - replace with actual API calls
const mockApiKeys = [
  {
    id: '1',
    name: 'Production API Key',
    key: 'sk_live_...',
    created: '2025-01-07',
    lastUsed: '2 hours ago',
    usage: 1234,
    status: 'active'
  },
  {
    id: '2',
    name: 'Development API Key',
    key: 'sk_test_...',
    created: '2025-01-05',
    lastUsed: '1 day ago',
    usage: 567,
    status: 'active'
  }
]

const mockUsageData = {
  daily: [
    { date: 'Jan 1', requests: 120, tokens: 45000 },
    { date: 'Jan 2', requests: 150, tokens: 58000 },
    { date: 'Jan 3', requests: 200, tokens: 72000 },
    { date: 'Jan 4', requests: 180, tokens: 65000 },
    { date: 'Jan 5', requests: 220, tokens: 85000 },
    { date: 'Jan 6', requests: 190, tokens: 70000 },
    { date: 'Jan 7', requests: 250, tokens: 95000 }
  ],
  total: {
    requests: 1310,
    tokens: 490000,
    cost: 24.50
  },
  limits: {
    requests: 10000,
    tokens: 1000000
  }
}

const mockProjects = [
  {
    id: '1',
    name: 'E-Commerce API',
    description: 'REST API for online store',
    created: '2025-01-06',
    lastModified: '1 hour ago',
    language: 'TypeScript',
    status: 'active',
    generations: 45
  },
  {
    id: '2',
    name: 'React Dashboard',
    description: 'Admin dashboard with charts',
    created: '2025-01-04',
    lastModified: '3 hours ago',
    language: 'React',
    status: 'active',
    generations: 32
  },
  {
    id: '3',
    name: 'Python ML Pipeline',
    description: 'Data processing pipeline',
    created: '2025-01-02',
    lastModified: '2 days ago',
    language: 'Python',
    status: 'completed',
    generations: 78
  }
]

export default function DashboardPage() {
  const router = useRouter()
  const [showKey, setShowKey] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    // Check authentication - redirect if not logged in
    const checkAuth = async () => {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        router.push('/login')
        return
      }
      // Fetch user data
      setUser({ name: 'John Doe', email: 'john@example.com', plan: 'Pro' })
    }
    checkAuth()
  }, [router])

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const generateNewKey = async () => {
    setIsLoading(true)
    // API call to generate new key
    setTimeout(() => {
      setIsLoading(false)
    }, 1000)
  }

  const deleteKey = async (id: string) => {
    // API call to delete key
    console.log('Deleting key:', id)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-500'
      case 'inactive': return 'text-gray-500'
      case 'expired': return 'text-red-500'
      default: return 'text-gray-500'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4" />
      case 'completed': return <CheckCircle className="h-4 w-4" />
      case 'inactive': return <XCircle className="h-4 w-4" />
      default: return <AlertCircle className="h-4 w-4" />
    }
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back, {user.name}! Manage your API keys, monitor usage, and track projects.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockUsageData.total.requests.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              +20.1% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tokens Used</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(mockUsageData.total.tokens / 1000).toFixed(0)}K</div>
            <p className="text-xs text-muted-foreground">
              {((mockUsageData.total.tokens / mockUsageData.limits.tokens) * 100).toFixed(0)}% of limit
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Projects</CardTitle>
            <Code2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockProjects.filter(p => p.status === 'active').length}</div>
            <p className="text-xs text-muted-foreground">
              {mockProjects.length} total projects
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Current Cost</CardTitle>
            <CreditCard className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${mockUsageData.total.cost.toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">
              {user.plan} Plan
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="api-keys">API Keys</TabsTrigger>
          <TabsTrigger value="projects">Projects</TabsTrigger>
          <TabsTrigger value="billing">Billing</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Usage Overview</CardTitle>
              <CardDescription>Your API usage over the last 7 days</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">API Requests</span>
                    <span className="text-sm text-muted-foreground">
                      {mockUsageData.total.requests} / {mockUsageData.limits.requests}
                    </span>
                  </div>
                  <Progress value={(mockUsageData.total.requests / mockUsageData.limits.requests) * 100} />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Token Usage</span>
                    <span className="text-sm text-muted-foreground">
                      {mockUsageData.total.tokens.toLocaleString()} / {mockUsageData.limits.tokens.toLocaleString()}
                    </span>
                  </div>
                  <Progress value={(mockUsageData.total.tokens / mockUsageData.limits.tokens) * 100} />
                </div>

                {/* Simple chart representation */}
                <div className="mt-6">
                  <h4 className="text-sm font-medium mb-4">Daily Requests</h4>
                  <div className="flex items-end justify-between h-32 gap-2">
                    {mockUsageData.daily.map((day, index) => (
                      <div key={index} className="flex-1 flex flex-col items-center">
                        <div
                          className="w-full bg-primary/20 hover:bg-primary/30 transition-colors rounded-t"
                          style={{ height: `${(day.requests / 250) * 100}%` }}
                        />
                        <span className="text-xs mt-2 text-muted-foreground">{day.date.split(' ')[1]}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Your latest code generations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Code2 className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">Generated authentication module</p>
                      <p className="text-xs text-muted-foreground">E-Commerce API • 2 hours ago</p>
                    </div>
                  </div>
                  <Badge variant="outline">TypeScript</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Code2 className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">Created dashboard components</p>
                      <p className="text-xs text-muted-foreground">React Dashboard • 3 hours ago</p>
                    </div>
                  </div>
                  <Badge variant="outline">React</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Code2 className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">Implemented data pipeline</p>
                      <p className="text-xs text-muted-foreground">Python ML Pipeline • 6 hours ago</p>
                    </div>
                  </div>
                  <Badge variant="outline">Python</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Keys Tab */}
        <TabsContent value="api-keys" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>API Keys</CardTitle>
                  <CardDescription>Manage your API keys for accessing Monkey Coder</CardDescription>
                </div>
                <Button onClick={generateNewKey} disabled={isLoading}>
                  <Plus className="h-4 w-4 mr-2" />
                  Generate New Key
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockApiKeys.map((apiKey) => (
                  <div key={apiKey.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium">{apiKey.name}</h4>
                        <Badge variant={apiKey.status === 'active' ? 'default' : 'secondary'}>
                          {apiKey.status}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span>Created: {apiKey.created}</span>
                        <span>Last used: {apiKey.lastUsed}</span>
                        <span>{apiKey.usage} requests</span>
                      </div>
                      <div className="flex items-center gap-2 mt-2">
                        <code className="bg-secondary px-2 py-1 rounded text-xs">
                          {showKey === apiKey.id ? 'sk_live_1234567890abcdef...' : apiKey.key}
                        </code>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => setShowKey(showKey === apiKey.id ? null : apiKey.id)}
                        >
                          {showKey === apiKey.id ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copyToClipboard('sk_live_1234567890abcdef...')}
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button size="sm" variant="ghost">
                        <RefreshCw className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => deleteKey(apiKey.id)}>
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>

              <Alert className="mt-4">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  Keep your API keys secure. Never share them publicly or commit them to version control.
                  You can regenerate keys at any time if they are compromised.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Projects Tab */}
        <TabsContent value="projects" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Projects</CardTitle>
                  <CardDescription>Your code generation projects</CardDescription>
                </div>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  New Project
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {mockProjects.map((project) => (
                  <Card key={project.id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-base">{project.name}</CardTitle>
                        <div className={getStatusColor(project.status)}>
                          {getStatusIcon(project.status)}
                        </div>
                      </div>
                      <CardDescription>{project.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center justify-between">
                          <span className="text-muted-foreground">Language:</span>
                          <Badge variant="outline">{project.language}</Badge>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-muted-foreground">Generations:</span>
                          <span>{project.generations}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-muted-foreground">Last modified:</span>
                          <span>{project.lastModified}</span>
                        </div>
                      </div>
                      <div className="flex gap-2 mt-4">
                        <Button size="sm" className="flex-1">Open</Button>
                        <Button size="sm" variant="outline" className="flex-1">Archive</Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Billing Tab */}
        <TabsContent value="billing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Billing & Subscription</CardTitle>
              <CardDescription>Manage your subscription and payment methods</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h4 className="font-medium">Current Plan: {user.plan}</h4>
                    <p className="text-sm text-muted-foreground">$79/month • Renews on Feb 7, 2025</p>
                  </div>
                  <Link href="/pricing">
                    <Button variant="outline">Change Plan</Button>
                  </Link>
                </div>

                <div>
                  <h4 className="font-medium mb-3">Current Usage</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span>Base subscription</span>
                      <span>$79.00</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span>Additional usage</span>
                      <span>$0.00</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span>GST (10%)</span>
                      <span>$7.90</span>
                    </div>
                    <div className="flex items-center justify-between font-medium pt-3 border-t">
                      <span>Total (AUD)</span>
                      <span>$86.90</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-3">Payment Method</h4>
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <CreditCard className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium">•••• •••• •••• 4242</p>
                        <p className="text-xs text-muted-foreground">Expires 12/25</p>
                      </div>
                    </div>
                    <Button size="sm" variant="outline">Update</Button>
                  </div>
                </div>

                <Button className="w-full">
                  Manage Billing in Stripe
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Account Settings</CardTitle>
              <CardDescription>Manage your account preferences</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="text-sm font-medium">Name</label>
                    <input
                      type="text"
                      className="w-full mt-1 px-3 py-2 border rounded-md"
                      defaultValue={user.name}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Email</label>
                    <input
                      type="email"
                      className="w-full mt-1 px-3 py-2 border rounded-md"
                      defaultValue={user.email}
                    />
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-3">Preferences</h4>
                  <div className="space-y-3">
                    <label className="flex items-center gap-2">
                      <input type="checkbox" defaultChecked />
                      <span className="text-sm">Email notifications for usage alerts</span>
                    </label>
                    <label className="flex items-center gap-2">
                      <input type="checkbox" defaultChecked />
                      <span className="text-sm">Weekly usage reports</span>
                    </label>
                    <label className="flex items-center gap-2">
                      <input type="checkbox" />
                      <span className="text-sm">Product updates and announcements</span>
                    </label>
                  </div>
                </div>

                <div className="flex gap-4">
                  <Button>Save Changes</Button>
                  <Button variant="outline">Cancel</Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-destructive">
            <CardHeader>
              <CardTitle className="text-destructive">Danger Zone</CardTitle>
              <CardDescription>Irreversible actions for your account</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="destructive">Delete Account</Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
