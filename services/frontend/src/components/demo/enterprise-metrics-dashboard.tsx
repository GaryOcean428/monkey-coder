"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  Activity, 
  TrendingUp, 
  Users, 
  Code2, 
  Shield, 
  Zap, 
  AlertTriangle,
  CheckCircle2,
  Clock,
  Server,
  Globe,
  Cpu,
  MemoryStick,
  Network,
  BarChart3,
  PieChart,
  LineChart
} from 'lucide-react'

interface MetricCard {
  title: string
  value: string
  change: string
  icon: React.ElementType
  trend: 'up' | 'down' | 'neutral'
}

interface SystemHealth {
  component: string
  status: 'healthy' | 'warning' | 'error'
  uptime: string
  lastCheck: string
}

const metrics: MetricCard[] = [
  {
    title: 'Total Code Generations',
    value: '47,892',
    change: '+12.5%',
    icon: Code2,
    trend: 'up'
  },
  {
    title: 'Active Users',
    value: '2,847',
    change: '+8.3%',
    icon: Users,
    trend: 'up'
  },
  {
    title: 'API Response Time',
    value: '142ms',
    change: '-5.2%',
    icon: Zap,
    trend: 'up'
  },
  {
    title: 'Security Score',
    value: '98.7%',
    change: '+0.3%',
    icon: Shield,
    trend: 'up'
  }
]

const systemHealth: SystemHealth[] = [
  {
    component: 'Orchestrator',
    status: 'healthy',
    uptime: '99.98%',
    lastCheck: '2 minutes ago'
  },
  {
    component: 'Quantum Executor',
    status: 'healthy',
    uptime: '99.95%',
    lastCheck: '1 minute ago'
  },
  {
    component: 'Persona Router',
    status: 'warning',
    uptime: '99.12%',
    lastCheck: '30 seconds ago'
  },
  {
    component: 'Provider Registry',
    status: 'healthy',
    uptime: '99.99%',
    lastCheck: '45 seconds ago'
  },
  {
    component: 'Security Framework',
    status: 'healthy',
    uptime: '100%',
    lastCheck: '1 minute ago'
  }
]

export function EnterpriseMetricsDashboard() {
  const [selectedTimeframe, setSelectedTimeframe] = useState('24h')
  const [realTimeData, setRealTimeData] = useState({
    cpuUsage: 23,
    memoryUsage: 67,
    networkIO: 45,
    activeConnections: 1247
  })

  useEffect(() => {
    const interval = setInterval(() => {
      setRealTimeData(prev => ({
        cpuUsage: Math.max(10, Math.min(90, prev.cpuUsage + (Math.random() - 0.5) * 10)),
        memoryUsage: Math.max(30, Math.min(85, prev.memoryUsage + (Math.random() - 0.5) * 8)),
        networkIO: Math.max(20, Math.min(80, prev.networkIO + (Math.random() - 0.5) * 15)),
        activeConnections: Math.max(800, Math.min(2000, prev.activeConnections + Math.floor((Math.random() - 0.5) * 50)))
      }))
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case 'error': return <AlertTriangle className="h-4 w-4 text-red-500" />
      default: return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500/10 text-green-600 border-green-500/20'
      case 'warning': return 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20'
      case 'error': return 'bg-red-500/10 text-red-600 border-red-500/20'
      default: return 'bg-gray-500/10 text-gray-600 border-gray-500/20'
    }
  }

  const getTrendIcon = (trend: string) => {
    return trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'
  }

  return (
    <section className="py-24 sm:py-32 bg-gradient-to-b from-secondary/5 to-background">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="text-base font-semibold leading-7 text-primary">
            Enterprise Monitoring
          </h2>
          <p className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
            Real-Time System Intelligence
          </p>
          <p className="mt-6 text-lg leading-8 text-muted-foreground">
            Monitor your AI code generation platform with enterprise-grade analytics, 
            performance metrics, and security insights in real-time.
          </p>
        </div>

        <Tabs value={selectedTimeframe} onValueChange={setSelectedTimeframe} className="w-full">
          <div className="flex items-center justify-between mb-8">
            <TabsList className="grid w-auto grid-cols-4">
              <TabsTrigger value="1h">1 Hour</TabsTrigger>
              <TabsTrigger value="24h">24 Hours</TabsTrigger>
              <TabsTrigger value="7d">7 Days</TabsTrigger>
              <TabsTrigger value="30d">30 Days</TabsTrigger>
            </TabsList>
            
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-muted-foreground">Live Data</span>
              </div>
            </div>
          </div>

          {/* Key Metrics Cards */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            {metrics.map((metric, index) => {
              const Icon = metric.icon
              return (
                <Card key={index} className="neon-card">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">
                      {metric.title}
                    </CardTitle>
                    <Icon className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{metric.value}</div>
                    <p className={`text-xs ${getTrendIcon(metric.trend)} flex items-center gap-1`}>
                      <TrendingUp className="h-3 w-3" />
                      {metric.change} from last {selectedTimeframe}
                    </p>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* System Health */}
            <Card className="neon-card lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-primary" />
                  System Health Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {systemHealth.map((component, index) => (
                    <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-secondary/20">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(component.status)}
                        <div>
                          <div className="font-medium">{component.component}</div>
                          <div className="text-sm text-muted-foreground">
                            Last check: {component.lastCheck}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge variant="outline" className={getStatusColor(component.status)}>
                          {component.status}
                        </Badge>
                        <div className="text-sm text-muted-foreground mt-1">
                          {component.uptime} uptime
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Real-time Performance */}
            <Card className="neon-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Server className="h-5 w-5 text-primary" />
                  Live Performance
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Cpu className="h-4 w-4" />
                      <span className="text-sm">CPU Usage</span>
                    </div>
                    <span className="text-sm font-medium">{realTimeData.cpuUsage.toFixed(1)}%</span>
                  </div>
                  <Progress value={realTimeData.cpuUsage} className="h-2" />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <MemoryStick className="h-4 w-4" />
                      <span className="text-sm">Memory</span>
                    </div>
                    <span className="text-sm font-medium">{realTimeData.memoryUsage.toFixed(1)}%</span>
                  </div>
                  <Progress value={realTimeData.memoryUsage} className="h-2" />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Network className="h-4 w-4" />
                      <span className="text-sm">Network I/O</span>
                    </div>
                    <span className="text-sm font-medium">{realTimeData.networkIO.toFixed(1)}%</span>
                  </div>
                  <Progress value={realTimeData.networkIO} className="h-2" />
                </div>

                <div className="pt-4 border-t">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Globe className="h-4 w-4" />
                      <span className="text-sm">Active Connections</span>
                    </div>
                    <span className="text-lg font-bold text-primary">
                      {realTimeData.activeConnections.toLocaleString()}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Analytics Tabs */}
          <div className="mt-8">
            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="security">Security</TabsTrigger>
                <TabsTrigger value="performance">Performance</TabsTrigger>
                <TabsTrigger value="usage">Usage Analytics</TabsTrigger>
              </TabsList>
              
              <TabsContent value="overview" className="mt-6">
                <div className="grid lg:grid-cols-2 gap-6">
                  <Card className="neon-card">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <BarChart3 className="h-5 w-5 text-primary" />
                        Code Generation Trends
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-48 flex items-center justify-center text-muted-foreground">
                        <div className="text-center">
                          <LineChart className="h-12 w-12 mx-auto mb-2 opacity-50" />
                          <p>Interactive charts showing generation volume, success rates, and model performance over time</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="neon-card">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <PieChart className="h-5 w-5 text-primary" />
                        Model Usage Distribution
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm">GPT-4.1</span>
                          <span className="text-sm font-medium">34.2%</span>
                        </div>
                        <Progress value={34.2} className="h-2" />
                        
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Claude 3.5 Sonnet</span>
                          <span className="text-sm font-medium">28.7%</span>
                        </div>
                        <Progress value={28.7} className="h-2" />
                        
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Gemini 2.5 Flash</span>
                          <span className="text-sm font-medium">19.3%</span>
                        </div>
                        <Progress value={19.3} className="h-2" />
                        
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Claude Opus 4.1</span>
                          <span className="text-sm font-medium">17.8%</span>
                        </div>
                        <Progress value={17.8} className="h-2" />
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="security" className="mt-6">
                <div className="grid lg:grid-cols-2 gap-6">
                  <Card className="neon-card">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Shield className="h-5 w-5 text-primary" />
                        Security Events (Last 24h)
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 rounded-lg bg-green-500/10">
                          <div className="flex items-center gap-3">
                            <CheckCircle2 className="h-4 w-4 text-green-500" />
                            <span className="text-sm">All security checks passed</span>
                          </div>
                          <Badge variant="outline" className="bg-green-500/10 text-green-600 border-green-500/20">
                            Clear
                          </Badge>
                        </div>
                        
                        <div className="text-center text-muted-foreground">
                          <Shield className="h-8 w-8 mx-auto mb-2 opacity-50" />
                          <p className="text-sm">No security incidents detected</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="neon-card">
                    <CardHeader>
                      <CardTitle>Threat Detection Score</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center">
                        <div className="text-4xl font-bold text-green-600 mb-2">98.7%</div>
                        <p className="text-sm text-muted-foreground mb-4">Security confidence score</p>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>SQL Injection Protection</span>
                            <span className="text-green-600">100%</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>XSS Prevention</span>
                            <span className="text-green-600">100%</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Rate Limiting</span>
                            <span className="text-green-600">98%</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Access Control</span>
                            <span className="text-green-600">100%</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="performance" className="mt-6">
                <Card className="neon-card">
                  <CardHeader>
                    <CardTitle>Performance Metrics</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-3 gap-6">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-primary mb-1">142ms</div>
                        <div className="text-sm text-muted-foreground">Avg Response Time</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-primary mb-1">99.98%</div>
                        <div className="text-sm text-muted-foreground">Uptime</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-primary mb-1">2,847</div>
                        <div className="text-sm text-muted-foreground">Req/min</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="usage" className="mt-6">
                <Card className="neon-card">
                  <CardHeader>
                    <CardTitle>Usage Analytics</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-medium mb-3">Top Languages Generated</h4>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-sm">TypeScript</span>
                            <span className="text-sm font-medium">32.1%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm">Python</span>
                            <span className="text-sm font-medium">28.4%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm">JavaScript</span>
                            <span className="text-sm font-medium">21.7%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm">Rust</span>
                            <span className="text-sm font-medium">17.8%</span>
                          </div>
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium mb-3">Peak Usage Hours</h4>
                        <div className="text-center">
                          <div className="text-lg font-bold text-primary">9 AM - 5 PM UTC</div>
                          <div className="text-sm text-muted-foreground mt-1">
                            Average 3.2K generations per hour
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </Tabs>

        {/* Call to Action */}
        <div className="mt-16 text-center">
          <p className="text-lg text-muted-foreground mb-6">
            Experience enterprise-grade monitoring and analytics for your development team
          </p>
          <div className="flex items-center justify-center gap-4">
            <Badge variant="outline" className="px-4 py-2">
              Real-time metrics
            </Badge>
            <Badge variant="outline" className="px-4 py-2">
              Advanced security
            </Badge>
            <Badge variant="outline" className="px-4 py-2">
              Performance insights
            </Badge>
          </div>
        </div>
      </div>
    </section>
  )
}