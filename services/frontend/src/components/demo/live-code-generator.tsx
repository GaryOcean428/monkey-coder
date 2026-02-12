"use client"

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Play, 
  Copy, 
  Code2, 
  Sparkles, 
  Zap, 
  CheckCircle,
  Loader2,
  FileText,
  Eye,
  RotateCcw
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface CodeExample {
  id: string
  title: string
  description: string
  prompt: string
  language: string
  complexity: 'simple' | 'moderate' | 'complex'
  category: string
  estimatedTime: string
}

const codeExamples: CodeExample[] = [
  {
    id: 'react-form',
    title: 'React Login Form',
    description: 'Create a responsive login form with validation',
    prompt: 'Create a React login form component with email and password fields, validation, and responsive design using Tailwind CSS',
    language: 'typescript',
    complexity: 'simple',
    category: 'Frontend',
    estimatedTime: '~15s'
  },
  {
    id: 'api-endpoint',
    title: 'REST API Endpoint',
    description: 'Build a user authentication API with Express.js',
    prompt: 'Create an Express.js API endpoint for user authentication with JWT tokens, password hashing, and input validation',
    language: 'javascript',
    complexity: 'moderate',
    category: 'Backend',
    estimatedTime: '~25s'
  },
  {
    id: 'python-algorithm',
    title: 'Sorting Algorithm',
    description: 'Implement an efficient sorting algorithm',
    prompt: 'Implement a quicksort algorithm in Python with detailed comments and time complexity analysis',
    language: 'python',
    complexity: 'moderate',
    category: 'Algorithm',
    estimatedTime: '~20s'
  }
]

const aiModels = [
  { id: 'gpt-4.1', name: 'GPT-4.1', speed: 'Fast', quality: 'High' },
  { id: 'claude-sonnet-4-5', name: 'Claude Sonnet 4.5', speed: 'Medium', quality: 'Excellent' },
  { id: 'claude-opus-4-6', name: 'Claude Opus 4.6', speed: 'Slow', quality: 'Superior' }
]

// Simulated code generation response
const simulatedResponse = `import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface LoginFormProps {
  onSubmit?: (email: string, password: string) => void
}

export function LoginForm({ onSubmit }: LoginFormProps) {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(false)

  const validateForm = () => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.email) {
      newErrors.email = 'Email is required'
    } else if (!validator.isEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email'
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    setIsLoading(true)
    
    try {
      await onSubmit?.(formData.email, formData.password)
    } catch (error) {
      console.error('Login failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold text-center">
          Welcome back
        </CardTitle>
        <p className="text-muted-foreground text-center">
          Enter your credentials to sign in
        </p>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="john@example.com"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              className={errors.email ? 'border-red-500' : ''}
              disabled={isLoading}
            />
            {errors.email && (
              <p className="text-sm text-red-500">{errors.email}</p>
            )}
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              value={formData.password}
              onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
              className={errors.password ? 'border-red-500' : ''}
              disabled={isLoading}
            />
            {errors.password && (
              <p className="text-sm text-red-500">{errors.password}</p>
            )}
          </div>
          
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? 'Signing in...' : 'Sign in'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}`

export function LiveCodeGenerator() {
  const [selectedExample, setSelectedExample] = useState<CodeExample>(codeExamples[0])
  const [selectedModel, setSelectedModel] = useState(aiModels[0])
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedCode, setGeneratedCode] = useState('')
  const [progress, setProgress] = useState(0)
  const [showOutput, setShowOutput] = useState(false)
  const [generationStats, setGenerationStats] = useState({
    tokensGenerated: 0,
    timeTaken: 0,
    linesOfCode: 0
  })

  const progressRef = useRef<NodeJS.Timeout>()

  const simulateCodeGeneration = async () => {
    setIsGenerating(true)
    setProgress(0)
    setGeneratedCode('')
    setShowOutput(false)

    const startTime = Date.now()

    // Simulate progressive generation
    let currentProgress = 0
    // Extract digits using string methods instead of regex (no-regex-by-default policy)
    const timeDigits = selectedExample.estimatedTime.split('').filter(char => char >= '0' && char <= '9').join('')
    const totalTime = parseInt(timeDigits) * 1000
    const interval = 100

    progressRef.current = setInterval(() => {
      currentProgress += (interval / totalTime) * 100
      if (currentProgress >= 100) {
        currentProgress = 100
        clearInterval(progressRef.current!)
        
        // Show final output
        setTimeout(() => {
          setGeneratedCode(simulatedResponse)
          setShowOutput(true)
          setIsGenerating(false)
          
          const endTime = Date.now()
          setGenerationStats({
            tokensGenerated: Math.floor(simulatedResponse.length / 4),
            timeTaken: (endTime - startTime) / 1000,
            linesOfCode: simulatedResponse.split('\n').length
          })
        }, 500)
      }
      setProgress(currentProgress)
    }, interval)
  }

  const copyToClipboard = async () => {
    if (generatedCode) {
      await navigator.clipboard.writeText(generatedCode)
    }
  }

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'simple': return 'bg-green-500/10 text-green-600 border-green-500/20'
      case 'moderate': return 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20'
      case 'complex': return 'bg-red-500/10 text-red-600 border-red-500/20'
      default: return 'bg-gray-500/10 text-gray-600 border-gray-500/20'
    }
  }

  useEffect(() => {
    return () => {
      if (progressRef.current) {
        clearInterval(progressRef.current)
      }
    }
  }, [])

  return (
    <section className="py-24 sm:py-32 bg-gradient-to-b from-background to-primary/5">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="text-base font-semibold leading-7 text-primary">
            Experience AI Code Generation
          </h2>
          <p className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
            Generate Production-Ready Code in Seconds
          </p>
          <p className="mt-6 text-lg leading-8 text-muted-foreground">
            Try our live demo to see how Monkey Coder transforms your ideas into clean, 
            well-documented code using advanced AI models.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Configuration Panel */}
          <Card className="neon-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                Code Generation Setup
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Example Selection */}
              <div className="space-y-3">
                <label className="text-sm font-medium">Choose Example</label>
                <div className="grid gap-3">
                  {codeExamples.map((example) => (
                    <div
                      key={example.id}
                      className={cn(
                        "p-4 rounded-lg border cursor-pointer transition-all hover:border-primary/50",
                        selectedExample.id === example.id
                          ? "border-primary bg-primary/5"
                          : "border-border hover:bg-secondary/50"
                      )}
                      onClick={() => setSelectedExample(example)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="font-medium">{example.title}</h3>
                        <div className="flex gap-2">
                          <Badge variant="outline" className={getComplexityColor(example.complexity)}>
                            {example.complexity}
                          </Badge>
                          <Badge variant="secondary">{example.category}</Badge>
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">
                        {example.description}
                      </p>
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Code2 className="h-3 w-3" />
                          {example.language}
                        </span>
                        <span className="flex items-center gap-1">
                          <Zap className="h-3 w-3" />
                          {example.estimatedTime}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Model Selection */}
              <div className="space-y-3">
                <label className="text-sm font-medium">AI Model</label>
                <Select value={selectedModel.id} onValueChange={(value) => 
                  setSelectedModel(aiModels.find(m => m.id === value) || aiModels[0])
                }>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {aiModels.map((model) => (
                      <SelectItem key={model.id} value={model.id}>
                        <div className="flex items-center justify-between w-full">
                          <span>{model.name}</span>
                          <div className="flex gap-2 ml-4">
                            <Badge variant="outline" className="text-xs">
                              {model.speed}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {model.quality}
                            </Badge>
                          </div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Generate Button */}
              <Button
                onClick={simulateCodeGeneration}
                disabled={isGenerating}
                className="w-full gap-2"
                size="lg"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Generating Code...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4" />
                    Generate Code
                  </>
                )}
              </Button>

              {/* Progress Bar */}
              {isGenerating && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Progress</span>
                    <span>{Math.round(progress)}%</span>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full transition-all duration-300 ease-out"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Output Panel */}
          <Card className="neon-card">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-primary" />
                  Generated Code
                </CardTitle>
                {showOutput && (
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={copyToClipboard}>
                      <Copy className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setShowOutput(false)}>
                      <RotateCcw className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {!showOutput && !isGenerating && (
                <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
                  <Eye className="h-12 w-12 mb-4 opacity-50" />
                  <p className="text-center">
                    Click "Generate Code" to see AI-generated code appear here
                  </p>
                </div>
              )}

              {isGenerating && (
                <div className="flex flex-col items-center justify-center h-64">
                  <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
                  <p className="text-center text-muted-foreground">
                    {selectedModel.name} is crafting your code...
                  </p>
                  <p className="text-sm text-muted-foreground mt-2">
                    Analyzing requirements and generating optimized code
                  </p>
                </div>
              )}

              {showOutput && (
                <div className="space-y-4">
                  <Tabs defaultValue="code" className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="code">Code</TabsTrigger>
                      <TabsTrigger value="stats">Statistics</TabsTrigger>
                    </TabsList>
                    <TabsContent value="code">
                      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono max-h-96 overflow-y-auto">
                        <code>{generatedCode}</code>
                      </pre>
                    </TabsContent>
                    <TabsContent value="stats">
                      <div className="grid grid-cols-3 gap-4">
                        <div className="text-center p-3 bg-secondary/50 rounded-lg">
                          <div className="text-2xl font-bold text-primary">
                            {generationStats.tokensGenerated}
                          </div>
                          <div className="text-xs text-muted-foreground">Tokens</div>
                        </div>
                        <div className="text-center p-3 bg-secondary/50 rounded-lg">
                          <div className="text-2xl font-bold text-primary">
                            {generationStats.timeTaken.toFixed(1)}s
                          </div>
                          <div className="text-xs text-muted-foreground">Time</div>
                        </div>
                        <div className="text-center p-3 bg-secondary/50 rounded-lg">
                          <div className="text-2xl font-bold text-primary">
                            {generationStats.linesOfCode}
                          </div>
                          <div className="text-xs text-muted-foreground">Lines</div>
                        </div>
                      </div>
                    </TabsContent>
                  </Tabs>

                  <div className="flex items-center gap-2 text-sm text-green-600">
                    <CheckCircle className="h-4 w-4" />
                    Code generated successfully with {selectedModel.name}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Call to Action */}
        <div className="mt-16 text-center">
          <p className="text-lg text-muted-foreground mb-6">
            Ready to integrate this into your workflow?
          </p>
          <div className="flex items-center justify-center gap-4">
            <Button size="lg" asChild>
              <a href="/getting-started">Get Started with CLI</a>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <a href="/signup">Create Free Account</a>
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}