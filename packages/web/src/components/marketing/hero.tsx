"use client"

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { ArrowRight, Code2, Sparkles, Zap, Terminal, Download, Key, CheckCircle } from 'lucide-react'
import { useState, useEffect } from 'react'

export function Hero() {
  const [currentStep, setCurrentStep] = useState(0)

  const cliSteps = [
    {
      command: '$ npm install -g monkey-coder-cli',
      description: 'Install the CLI globally',
      icon: Download,
      output: '✓ Installed monkey-coder-cli@1.0.0'
    },
    {
      command: '$ monkey-coder --version',
      description: 'Verify installation',
      icon: CheckCircle,
      output: 'monkey-coder-cli v1.0.0'
    },
    {
      command: '$ monkey-coder config set apiKey "your-key"',
      description: 'Configure your API key',
      icon: Key,
      output: '✓ API key configured successfully'
    },
    {
      command: '$ monkey-coder implement "Create a React login form"',
      description: 'Generate your first component',
      icon: Code2,
      output: '✓ Generated: LoginForm.tsx (45 lines)'
    }
  ]

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % cliSteps.length)
    }, 4000)
    return () => clearInterval(timer)
  }, [cliSteps.length])

  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-background to-primary/5">
      <div className="absolute inset-0 bg-grid-black/[0.02] -z-10" />
      <div className="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8 lg:py-40">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-8 flex justify-center">
            <div className="relative rounded-full px-3 py-1 text-sm leading-6 text-muted-foreground ring-1 ring-gray-900/10 hover:ring-gray-900/20 dark:ring-gray-100/10 dark:hover:ring-gray-100/20">
              Powered by Claude Opus 4.1, GPT-4.1, and more{' '}
              <Link href="/getting-started" className="font-semibold text-primary">
                <span className="absolute inset-0" aria-hidden="true" />
                Get started <span aria-hidden="true">&rarr;</span>
              </Link>
            </div>
          </div>

          <h1 className="text-4xl font-bold tracking-tight sm:text-6xl animate-fade-up">
            Transform ideas into
            <span className="bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
              {' '}production-ready code
            </span>
          </h1>

          <p className="mt-6 text-lg leading-8 text-muted-foreground animate-fade-up animation-delay-100">
            Install our CLI in seconds and start generating code with advanced AI models.
            From React components to complete APIs - build faster with AI assistance.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-x-6 gap-y-4 animate-fade-up animation-delay-200">
            <Link href="/getting-started">
              <Button size="lg" className="gap-2">
                <Terminal className="h-4 w-4" />
                Install CLI Now
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/signup">
              <Button variant="outline" size="lg">
                Create Free Account
              </Button>
            </Link>
          </div>

          {/* Sign in for existing users */}
          <div className="mt-6 text-center animate-fade-up animation-delay-300">
            <p className="text-sm text-muted-foreground">
              Already have an account?{' '}
              <Link href="/login" className="font-medium text-primary hover:text-primary/80 transition-colors">
                Sign in →
              </Link>
            </p>
          </div>

          <div className="mt-10 flex items-center justify-center gap-x-8 text-sm text-muted-foreground animate-fade-up animation-delay-400">
            <div className="flex items-center gap-2">
              <Code2 className="h-4 w-4" />
              <span>358+ languages</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4" />
              <span>Lightning fast</span>
            </div>
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              <span>AI-powered</span>
            </div>
          </div>
        </div>

        {/* Interactive CLI Demo */}
        <div className="mt-16 flow-root sm:mt-24">
          <div className="relative rounded-xl bg-gray-900/5 p-2 ring-1 ring-inset ring-gray-900/10 lg:-m-4 lg:rounded-2xl lg:p-4">
            <div className="rounded-md bg-gray-900 shadow-2xl ring-1 ring-white/10">
              {/* Terminal Header */}
              <div className="flex items-center justify-between border-b border-gray-800 px-4 py-2">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-red-500" />
                  <div className="h-3 w-3 rounded-full bg-yellow-500" />
                  <div className="h-3 w-3 rounded-full bg-green-500" />
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-400">
                  <Terminal className="h-3 w-3" />
                  <span>Terminal - monkey-coder-cli</span>
                </div>
              </div>

              {/* Terminal Content */}
              <div className="p-4 font-mono text-sm">
                {/* Step Indicator */}
                <div className="mb-4 flex items-center gap-2">
                  {cliSteps.map((step, index) => {
                    const Icon = step.icon
                    return (
                      <div
                        key={index}
                        className={`flex items-center justify-center rounded-full p-1.5 transition-all duration-500 ${
                          index === currentStep
                            ? 'bg-primary text-primary-foreground scale-110'
                            : index < currentStep
                            ? 'bg-green-600 text-white'
                            : 'bg-gray-700 text-gray-400'
                        }`}
                      >
                        <Icon className="h-3 w-3" />
                      </div>
                    )
                  })}
                </div>

                {/* Current Command */}
                <div className="space-y-3">
                  <div className="text-gray-400 text-xs">
                    {cliSteps[currentStep].description}
                  </div>
                  <div className="text-green-400">
                    <span className="animate-pulse">{cliSteps[currentStep].command}</span>
                  </div>
                  <div className="text-gray-300 opacity-0 animate-fade-in animation-delay-200">
                    {cliSteps[currentStep].output}
                  </div>
                </div>

                {/* Quick Start Hint */}
                <div className="mt-6 border-t border-gray-800 pt-4">
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span>Ready to start?</span>
                    <Link href="/getting-started" className="text-primary hover:underline">
                      Follow our step-by-step guide →
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
