"use client"

import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Check,
  Copy,
  Terminal,
  Key,
  Zap,
  ChevronRight,
  Package,
  Settings,
  Rocket,
  AlertCircle,
  CheckCircle2,
  Command
} from 'lucide-react'
import { toast } from 'react-hot-toast'

export default function GettingStartedPage() {
  const [copiedCommand, setCopiedCommand] = useState<string | null>(null)
  const [completedSteps, setCompletedSteps] = useState<string[]>([])

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text)
    setCopiedCommand(label)
    toast.success(`Copied ${label} to clipboard!`)
    setTimeout(() => setCopiedCommand(null), 2000)
  }

  const markStepComplete = (stepId: string) => {
    if (!completedSteps.includes(stepId)) {
      setCompletedSteps([...completedSteps, stepId])
    }
  }

  const steps = [
    { id: 'install', title: 'Install CLI', icon: Package },
    { id: 'verify', title: 'Verify Installation', icon: CheckCircle2 },
    { id: 'account', title: 'Create Account', icon: Key },
    { id: 'configure', title: 'Configure API', icon: Settings },
    { id: 'first-command', title: 'First Command', icon: Rocket }
  ]

  return (
    <div className="container mx-auto py-16 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Getting Started with Monkey Coder CLI</h1>
          <p className="text-lg text-muted-foreground">
            Follow this step-by-step guide to install, configure, and start using the Monkey Coder CLI
          </p>
        </div>

        {/* Progress Tracker */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Your Progress</CardTitle>
            <CardDescription>Complete each step to get up and running</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              {steps.map((step, index) => {
                const Icon = step.icon
                const isCompleted = completedSteps.includes(step.id)
                return (
                  <div key={step.id} className="flex items-center">
                    <div className="flex flex-col items-center">
                      <div className={`rounded-full p-3 ${
                        isCompleted
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-secondary text-secondary-foreground'
                      }`}>
                        {isCompleted ? <Check className="h-5 w-5" /> : <Icon className="h-5 w-5" />}
                      </div>
                      <span className="text-xs mt-2 text-center">{step.title}</span>
                    </div>
                    {index < steps.length - 1 && (
                      <ChevronRight className="h-5 w-5 mx-4 text-muted-foreground" />
                    )}
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Step 1: Installation */}
        <Card className="mb-8" id="install">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Package className="h-8 w-8 text-primary" />
                <div>
                  <CardTitle>Step 1: Install Monkey Coder CLI</CardTitle>
                  <CardDescription>Choose your preferred package manager</CardDescription>
                </div>
              </div>
              {completedSteps.includes('install') && (
                <CheckCircle2 className="h-6 w-6 text-green-500" />
              )}
            </div>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="npm" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="npm">npm</TabsTrigger>
                <TabsTrigger value="yarn">Yarn</TabsTrigger>
                <TabsTrigger value="pnpm">pnpm</TabsTrigger>
                <TabsTrigger value="homebrew">Homebrew</TabsTrigger>
              </TabsList>

              <TabsContent value="npm">
                <div className="space-y-4">
                  <div className="relative">
                    <pre className="bg-secondary p-4 rounded-lg overflow-x-auto">
                      <code>npm install -g monkey-coder-cli</code>
                    </pre>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="absolute top-2 right-2"
                      onClick={() => copyToClipboard('npm install -g monkey-coder-cli', 'npm install command')}
                    >
                      {copiedCommand === 'npm install command' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                    </Button>
                  </div>
                  <Alert>
                    <Terminal className="h-4 w-4" />
                    <AlertDescription>
                      Requires Node.js 18.0 or higher. Run <code>node --version</code> to check.
                    </AlertDescription>
                  </Alert>
                </div>
              </TabsContent>

              <TabsContent value="yarn">
                <div className="space-y-4">
                  <div className="relative">
                    <pre className="bg-secondary p-4 rounded-lg overflow-x-auto">
                      <code>yarn global add monkey-coder-cli</code>
                    </pre>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="absolute top-2 right-2"
                      onClick={() => copyToClipboard('yarn global add monkey-coder-cli', 'yarn install command')}
                    >
                      {copiedCommand === 'yarn install command' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="pnpm">
                <div className="space-y-4">
                  <div className="relative">
                    <pre className="bg-secondary p-4 rounded-lg overflow-x-auto">
                      <code>pnpm add -g monkey-coder-cli</code>
                    </pre>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="absolute top-2 right-2"
                      onClick={() => copyToClipboard('pnpm add -g monkey-coder-cli', 'pnpm install command')}
                    >
                      {copiedCommand === 'pnpm install command' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="homebrew">
                <div className="space-y-4">
                  <div className="relative">
                    <pre className="bg-secondary p-4 rounded-lg overflow-x-auto">
                      <code>brew install monkey-coder-cli</code>
                    </pre>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="absolute top-2 right-2"
                      onClick={() => copyToClipboard('brew install monkey-coder-cli', 'brew install command')}
                    >
                      {copiedCommand === 'brew install command' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                    </Button>
                  </div>
                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      macOS and Linux only. Requires Homebrew to be installed.
                    </AlertDescription>
                  </Alert>
                </div>
              </TabsContent>
            </Tabs>

            <div className="mt-4 flex justify-end">
              <Button
                variant="outline"
                size="sm"
                onClick={() => markStepComplete('install')}
              >
                Mark as Complete
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Step 2: Verify Installation */}
        <Card className="mb-8" id="verify">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-8 w-8 text-primary" />
                <div>
                  <CardTitle>Step 2: Verify Installation</CardTitle>
                  <CardDescription>Make sure the CLI is installed correctly</CardDescription>
                </div>
              </div>
              {completedSteps.includes('verify') && (
                <CheckCircle2 className="h-6 w-6 text-green-500" />
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="relative">
              <pre className="bg-secondary p-4 rounded-lg overflow-x-auto">
                <code>monkey-coder --version</code>
              </pre>
              <Button
                size="sm"
                variant="ghost"
                className="absolute top-2 right-2"
                onClick={() => copyToClipboard('monkey-coder --version', 'version command')}
              >
                {copiedCommand === 'version command' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>

            <div className="bg-secondary/50 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">Expected output:</p>
              <pre className="text-sm">
                <code>monkey-coder-cli v1.0.0</code>
              </pre>
            </div>

            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                If the command is not found, you may need to restart your terminal or add the global npm/yarn directory to your PATH.
              </AlertDescription>
            </Alert>

            <div className="flex justify-end">
              <Button
                variant="outline"
                size="sm"
                onClick={() => markStepComplete('verify')}
              >
                Mark as Complete
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Step 3: Create Account & Get API Key */}
        <Card className="mb-8" id="account">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Key className="h-8 w-8 text-primary" />
                <div>
                  <CardTitle>Step 3: Create Account & Get API Key</CardTitle>
                  <CardDescription>Sign up and generate your API key</CardDescription>
                </div>
              </div>
              {completedSteps.includes('account') && (
                <CheckCircle2 className="h-6 w-6 text-green-500" />
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">1. Create Account</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    Sign up for a free account to get started
                  </p>
                  <Link href="/signup">
                    <Button className="w-full">
                      Create Free Account
                    </Button>
                  </Link>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">2. Generate API Key</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    Access your dashboard to create an API key
                  </p>
                  <Link href="/api-keys">
                    <Button variant="outline" className="w-full">
                      Go to API Keys
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </div>

            <Alert>
              <Key className="h-4 w-4" />
              <AlertDescription>
                Keep your API key secure! Never share it publicly or commit it to version control.
              </AlertDescription>
            </Alert>

            <div className="flex justify-end">
              <Button
                variant="outline"
                size="sm"
                onClick={() => markStepComplete('account')}
              >
                Mark as Complete
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Step 4: Configure API Key */}
        <Card className="mb-8" id="configure">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Settings className="h-8 w-8 text-primary" />
                <div>
                  <CardTitle>Step 4: Configure Your API Key</CardTitle>
                  <CardDescription>Connect the CLI to your account</CardDescription>
                </div>
              </div>
              {completedSteps.includes('configure') && (
                <CheckCircle2 className="h-6 w-6 text-green-500" />
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium mb-2">Set your API key:</p>
                <div className="relative">
                  <pre className="bg-secondary p-4 rounded-lg overflow-x-auto">
                    <code>monkey-coder config set apiKey "your-api-key-here"</code>
                  </pre>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="absolute top-2 right-2"
                    onClick={() => copyToClipboard('monkey-coder config set apiKey "your-api-key-here"', 'config command')}
                  >
                    {copiedCommand === 'config command' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              <div>
                <p className="text-sm font-medium mb-2">Verify configuration:</p>
                <div className="relative">
                  <pre className="bg-secondary p-4 rounded-lg overflow-x-auto">
                    <code>monkey-coder config list</code>
                  </pre>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="absolute top-2 right-2"
                    onClick={() => copyToClipboard('monkey-coder config list', 'list config command')}
                  >
                    {copiedCommand === 'list config command' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              <div>
                <p className="text-sm font-medium mb-2">Test connection:</p>
                <div className="relative">
                  <pre className="bg-secondary p-4 rounded-lg overflow-x-auto">
                    <code>monkey-coder health</code>
                  </pre>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="absolute top-2 right-2"
                    onClick={() => copyToClipboard('monkey-coder health', 'health command')}
                  >
                    {copiedCommand === 'health command' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
            </div>

            <Alert>
              <Settings className="h-4 w-4" />
              <AlertDescription>
                Your configuration is stored locally at <code>~/.config/monkey-coder/config.json</code>
              </AlertDescription>
            </Alert>

            <div className="flex justify-end">
              <Button
                variant="outline"
                size="sm"
                onClick={() => markStepComplete('configure')}
              >
                Mark as Complete
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Step 5: Run Your First Command */}
        <Card className="mb-8" id="first-command">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Rocket className="h-8 w-8 text-primary" />
                <div>
                  <CardTitle>Step 5: Run Your First Command</CardTitle>
                  <CardDescription>Start generating code with AI</CardDescription>
                </div>
              </div>
              {completedSteps.includes('first-command') && (
                <CheckCircle2 className="h-6 w-6 text-green-500" />
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <Tabs defaultValue="simple" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="simple">Simple Example</TabsTrigger>
                <TabsTrigger value="react">React Component</TabsTrigger>
                <TabsTrigger value="api">API Endpoint</TabsTrigger>
              </TabsList>

              <TabsContent value="simple" className="space-y-4">
                <div className="relative">
                  <pre className="bg-secondary p-4 rounded-lg overflow-x-auto">
                    <code>monkey-coder implement "Create a function to validate email addresses" --output email-validator.js</code>
                  </pre>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="absolute top-2 right-2"
                    onClick={() => copyToClipboard('monkey-coder implement "Create a function to validate email addresses" --output email-validator.js', 'simple example')}
                  >
                    {copiedCommand === 'simple example' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </div>
                <div className="bg-secondary/50 p-4 rounded-lg">
                  <p className="text-sm text-muted-foreground mb-2">This will generate:</p>
                  <pre className="text-sm">
                    <code>{`// email-validator.js
function validateEmail(email) {
  const regex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
  return regex.test(email);
}`}</code>
                  </pre>
                </div>
              </TabsContent>

              <TabsContent value="react" className="space-y-4">
                <div className="relative">
                  <pre className="bg-secondary p-4 rounded-lg overflow-x-auto">
                    <code>monkey-coder implement "Create a React login form component with validation" --language typescript --output LoginForm.tsx</code>
                  </pre>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="absolute top-2 right-2"
                    onClick={() => copyToClipboard('monkey-coder implement "Create a React login form component with validation" --language typescript --output LoginForm.tsx', 'react example')}
                  >
                    {copiedCommand === 'react example' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </div>
              </TabsContent>

              <TabsContent value="api" className="space-y-4">
                <div className="relative">
                  <pre className="bg-secondary p-4 rounded-lg overflow-x-auto">
                    <code>monkey-coder implement "Create a REST API endpoint for user authentication" --persona architect --stream</code>
                  </pre>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="absolute top-2 right-2"
                    onClick={() => copyToClipboard('monkey-coder implement "Create a REST API endpoint for user authentication" --persona architect --stream', 'api example')}
                  >
                    {copiedCommand === 'api example' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </div>
              </TabsContent>
            </Tabs>

            <div className="flex justify-end">
              <Button
                variant="outline"
                size="sm"
                onClick={() => markStepComplete('first-command')}
              >
                Mark as Complete
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Success Message */}
        {completedSteps.length === steps.length && (
          <Card className="border-green-500 bg-green-50 dark:bg-green-950/20">
            <CardHeader>
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-8 w-8 text-green-500" />
                <div>
                  <CardTitle>Congratulations! 🎉</CardTitle>
                  <CardDescription>You've successfully set up Monkey Coder CLI</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="mb-4">You're now ready to accelerate your development with AI-powered code generation!</p>
              <div className="flex gap-4">
                <Link href="/docs/cli">
                  <Button>
                    View Full Documentation
                  </Button>
                </Link>
                <Link href="/dashboard">
                  <Button variant="outline">
                    Go to Dashboard
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Quick Reference */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Quick Command Reference</CardTitle>
            <CardDescription>Common commands for daily use</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold mb-2 flex items-center gap-2">
                  <Command className="h-4 w-4" />
                  Code Generation
                </h4>
                <div className="space-y-2 text-sm">
                  <code className="block bg-secondary p-2 rounded">monkey-coder implement [prompt]</code>
                  <code className="block bg-secondary p-2 rounded">monkey-coder analyze [files]</code>
                  <code className="block bg-secondary p-2 rounded">monkey-coder test [files]</code>
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-2 flex items-center gap-2">
                  <Settings className="h-4 w-4" />
                  Configuration
                </h4>
                <div className="space-y-2 text-sm">
                  <code className="block bg-secondary p-2 rounded">monkey-coder config set [key] [value]</code>
                  <code className="block bg-secondary p-2 rounded">monkey-coder config list</code>
                  <code className="block bg-secondary p-2 rounded">monkey-coder health</code>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Help Section */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Need Help?</CardTitle>
            <CardDescription>Resources and support</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              <Link href="/docs/cli">
                <Button variant="outline" className="w-full">
                  📚 Documentation
                </Button>
              </Link>
              <Link href="/contact">
                <Button variant="outline" className="w-full">
                  💬 Contact Support
                </Button>
              </Link>
              <Link href="https://github.com/GaryOcean428/monkey-coder/issues">
                <Button variant="outline" className="w-full">
                  🐛 Report Issue
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
