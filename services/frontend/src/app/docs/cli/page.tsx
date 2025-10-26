"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Terminal,
  Code2,
  FileSearch,
  Building,
  TestTube,
  Settings,
  Heart,
  Copy,
  Check,
  Info,
  Shield,
  Zap,
  FileText
} from 'lucide-react'
import { useState } from 'react'
import Link from 'next/link'

export default function CLIDocsPage() {
  const [copiedCommand, setCopiedCommand] = useState<string | null>(null)

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text)
    setCopiedCommand(label)
    setTimeout(() => setCopiedCommand(null), 2000)
  }

  const commands = [
    {
      name: 'implement',
      icon: Code2,
      description: 'Generate code implementation based on requirements',
      category: 'Core',
      examples: [
        {
          command: 'monkey-coder implement "Create a user authentication system"',
          description: 'Basic implementation'
        },
        {
          command: 'monkey-coder implement "Add error handling" src/api.ts --output src/api-fixed.ts',
          description: 'Modify existing file'
        },
        {
          command: 'monkey-coder implement "Convert to TypeScript" legacy.js --language typescript --stream',
          description: 'Language conversion with streaming'
        }
      ],
      options: [
        { flag: '-o, --output', description: 'Output file path' },
        { flag: '-l, --language', description: 'Target programming language' },
        { flag: '-p, --persona', description: 'AI persona to use (developer, architect, etc.)' },
        { flag: '--model', description: 'Specific AI model to use' },
        { flag: '--stream', description: 'Enable streaming output' },
        { flag: '-t, --temperature', description: 'Model temperature (0.0-2.0)' }
      ]
    },
    {
      name: 'analyze',
      icon: FileSearch,
      description: 'Analyze code for quality, security, and performance issues',
      category: 'Core',
      examples: [
        {
          command: 'monkey-coder analyze src/**/*.ts --type security',
          description: 'Security analysis'
        },
        {
          command: 'monkey-coder analyze app.py --type performance --output report.md',
          description: 'Performance analysis with report'
        }
      ],
      options: [
        { flag: '-t, --type', description: 'Analysis type (quality, security, performance)' },
        { flag: '-o, --output', description: 'Output file for analysis report' },
        { flag: '-p, --persona', description: 'AI persona (default: reviewer)' },
        { flag: '--stream', description: 'Enable streaming output' }
      ]
    },
    {
      name: 'build',
      icon: Building,
      description: 'Build and optimize code architecture',
      category: 'Core',
      examples: [
        {
          command: 'monkey-coder build "Design a microservices architecture"',
          description: 'Architecture design'
        },
        {
          command: 'monkey-coder build "Refactor monolith" src/ --output refactored/',
          description: 'Refactoring with output directory'
        }
      ],
      options: [
        { flag: '-o, --output', description: 'Output directory for built files' },
        { flag: '-p, --persona', description: 'AI persona (default: architect)' },
        { flag: '--stream', description: 'Enable streaming output' }
      ]
    },
    {
      name: 'test',
      icon: TestTube,
      description: 'Generate comprehensive tests for your code',
      category: 'Core',
      examples: [
        {
          command: 'monkey-coder test src/utils.ts --framework jest',
          description: 'Generate Jest tests'
        },
        {
          command: 'monkey-coder test src/**/*.py --output tests/ --framework pytest',
          description: 'Generate Python tests'
        }
      ],
      options: [
        { flag: '-o, --output', description: 'Output directory for test files' },
        { flag: '-f, --framework', description: 'Testing framework (jest, pytest, etc.)' },
        { flag: '-p, --persona', description: 'AI persona (default: tester)' },
        { flag: '--stream', description: 'Enable streaming output' }
      ]
    },
    {
      name: 'config',
      icon: Settings,
      description: 'Manage CLI configuration',
      category: 'Config',
      examples: [
        {
          command: 'monkey-coder config set apiKey "your-api-key"',
          description: 'Set API key'
        },
        {
          command: 'monkey-coder config list',
          description: 'List all configuration'
        },
        {
          command: 'monkey-coder config reset',
          description: 'Reset to defaults'
        }
      ],
      options: [
        { flag: 'set <key> <value>', description: 'Set a configuration value' },
        { flag: 'get <key>', description: 'Get a configuration value' },
        { flag: 'list', description: 'List all configuration' },
        { flag: 'reset', description: 'Reset to default configuration' }
      ]
    },
    {
      name: 'health',
      icon: Heart,
      description: 'Check API server health status',
      category: 'Utility',
      examples: [
        {
          command: 'monkey-coder health',
          description: 'Check server status'
        }
      ],
      options: []
    }
  ]

  const personas = [
    { name: 'developer', icon: Code2, description: 'General purpose coding and implementation' },
    { name: 'architect', icon: Building, description: 'System design and architecture planning' },
    { name: 'reviewer', icon: FileSearch, description: 'Code review and quality analysis' },
    { name: 'security_analyst', icon: Shield, description: 'Security-focused analysis' },
    { name: 'performance_expert', icon: Zap, description: 'Performance optimization' },
    { name: 'tester', icon: TestTube, description: 'Test generation and quality assurance' },
    { name: 'technical_writer', icon: FileText, description: 'Documentation and explanation' }
  ]

  return (
    <div className="container mx-auto py-16 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold mb-4">CLI Documentation</h1>
          <p className="text-lg text-muted-foreground">
            Complete reference for the Monkey Coder CLI commands, options, and usage patterns
          </p>
          <div className="mt-4 flex gap-4">
            <Link href="/getting-started">
              <Button variant="outline">
                <Terminal className="h-4 w-4 mr-2" />
                Getting Started Guide
              </Button>
            </Link>
            <Link href="https://github.com/GaryOcean428/monkey-coder">
              <Button variant="outline">
                View on GitHub
              </Button>
            </Link>
          </div>
        </div>

        {/* Quick Install */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Quick Install (Recommended)</CardTitle>
            <CardDescription>Activate Yarn via Corepack and run the CLI with <code>yarn dlx</code></CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="relative">
                <pre className="bg-secondary p-4 rounded-lg overflow-x-auto">
                  <code>corepack enable &amp;&amp; corepack prepare yarn@4.9.2 --activate</code>
                </pre>
                <Button
                  size="sm"
                  variant="ghost"
                  className="absolute top-2 right-2"
                  onClick={() => copyToClipboard('corepack enable && corepack prepare yarn@4.9.2 --activate', 'corepack setup')}
                >
                  {copiedCommand === 'corepack setup' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                </Button>
              </div>
              <div className="relative">
                <pre className="bg-secondary p-4 rounded-lg overflow-x-auto">
                  <code>yarn dlx monkey-coder-cli@latest --help</code>
                </pre>
                <Button
                  size="sm"
                  variant="ghost"
                  className="absolute top-2 right-2"
                  onClick={() => copyToClipboard('yarn dlx monkey-coder-cli@latest --help', 'yarn dlx install')}
                >
                  {copiedCommand === 'yarn dlx install' ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                </Button>
              </div>
              <Alert>
                <Terminal className="h-4 w-4" />
                <AlertDescription>
                  Need legacy npm or global installs? They still work, but we now recommend <code>yarn dlx</code> to stay aligned with the Yarn 4 workspace toolchain.
                </AlertDescription>
              </Alert>
            </div>
          </CardContent>
        </Card>

        {/* Commands Reference */}
        <Tabs defaultValue="all" className="mb-8">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="all">All Commands</TabsTrigger>
            <TabsTrigger value="core">Core</TabsTrigger>
            <TabsTrigger value="config">Config</TabsTrigger>
            <TabsTrigger value="utility">Utility</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="space-y-6">
            {commands.map((cmd) => (
              <CommandCard key={cmd.name} command={cmd} copyToClipboard={copyToClipboard} copiedCommand={copiedCommand} />
            ))}
          </TabsContent>

          <TabsContent value="core" className="space-y-6">
            {commands.filter(cmd => cmd.category === 'Core').map((cmd) => (
              <CommandCard key={cmd.name} command={cmd} copyToClipboard={copyToClipboard} copiedCommand={copiedCommand} />
            ))}
          </TabsContent>

          <TabsContent value="config" className="space-y-6">
            {commands.filter(cmd => cmd.category === 'Config').map((cmd) => (
              <CommandCard key={cmd.name} command={cmd} copyToClipboard={copyToClipboard} copiedCommand={copiedCommand} />
            ))}
          </TabsContent>

          <TabsContent value="utility" className="space-y-6">
            {commands.filter(cmd => cmd.category === 'Utility').map((cmd) => (
              <CommandCard key={cmd.name} command={cmd} copyToClipboard={copyToClipboard} copiedCommand={copiedCommand} />
            ))}
          </TabsContent>
        </Tabs>

        {/* AI Personas */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>AI Personas</CardTitle>
            <CardDescription>Choose specialized AI personas for different tasks</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              {personas.map((persona) => {
                const Icon = persona.icon
                return (
                  <div key={persona.name} className="flex items-start gap-3 p-3 rounded-lg border">
                    <Icon className="h-5 w-5 text-primary mt-0.5" />
                    <div>
                      <code className="text-sm font-semibold">{persona.name}</code>
                      <p className="text-sm text-muted-foreground mt-1">{persona.description}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Configuration */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Configuration Options</CardTitle>
            <CardDescription>Available configuration keys and their defaults</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <ConfigOption name="apiKey" type="string" description="Your API key for authentication" />
              <ConfigOption name="baseUrl" type="string" default="https://monkey-coder.up.railway.app" description="Base URL for the API" />
              <ConfigOption name="defaultPersona" type="string" default="developer" description="Default AI persona" />
              <ConfigOption name="defaultModel" type="string" default="claude-opus-4-1-20250805" description="Default AI model" />
              <ConfigOption name="defaultProvider" type="string" default="anthropic" description="Default AI provider" />
              <ConfigOption name="defaultTemperature" type="number" default="0.1" description="Default model temperature" />
              <ConfigOption name="defaultTimeout" type="number" default="300" description="Default request timeout (seconds)" />
            </div>
          </CardContent>
        </Card>

        {/* Environment Variables */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Environment Variables</CardTitle>
            <CardDescription>Alternative configuration through environment variables</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-3 rounded-lg bg-secondary">
                <code className="text-sm">MONKEY_CODER_API_KEY</code>
                <span className="text-sm text-muted-foreground">API key</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-secondary">
                <code className="text-sm">MONKEY_CODER_API_URL</code>
                <span className="text-sm text-muted-foreground">Base URL for the API</span>
              </div>
            </div>
            <Alert className="mt-4">
              <Info className="h-4 w-4" />
              <AlertDescription>
                Environment variables take precedence over configuration file settings
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        {/* Advanced Usage */}
        <Card>
          <CardHeader>
            <CardTitle>Advanced Usage Patterns</CardTitle>
            <CardDescription>Pro tips and advanced workflows</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">Streaming Output</h4>
              <p className="text-sm text-muted-foreground mb-2">
                Use the --stream flag for real-time progress updates on long-running tasks:
              </p>
              <pre className="bg-secondary p-3 rounded-lg text-sm">
                <code>monkey-coder implement "Complex system" --stream</code>
              </pre>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Combining Commands</h4>
              <p className="text-sm text-muted-foreground mb-2">
                Chain commands for complete workflows:
              </p>
              <pre className="bg-secondary p-3 rounded-lg text-sm">
                <code>{`# Generate code, analyze it, then create tests
monkey-coder implement "API endpoint" --output api.ts
monkey-coder analyze api.ts --type security
monkey-coder test api.ts --framework jest`}</code>
              </pre>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Using Personas Effectively</h4>
              <p className="text-sm text-muted-foreground mb-2">
                Match personas to tasks for best results:
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <Badge variant="outline">architect</Badge>
                  <span className="text-muted-foreground">for system design</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Badge variant="outline">security_analyst</Badge>
                  <span className="text-muted-foreground">for vulnerability checks</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Badge variant="outline">performance_expert</Badge>
                  <span className="text-muted-foreground">for optimization</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function CommandCard({ command, copyToClipboard, copiedCommand }: any) {
  const Icon = command.icon

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Icon className="h-6 w-6 text-primary" />
            <div>
              <CardTitle className="text-xl">
                <code>monkey-coder {command.name}</code>
              </CardTitle>
              <CardDescription>{command.description}</CardDescription>
            </div>
          </div>
          <Badge>{command.category}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Examples */}
        {command.examples.length > 0 && (
          <div>
            <h4 className="font-semibold mb-2">Examples</h4>
            <div className="space-y-2">
              {command.examples.map((example: any, index: number) => (
                <div key={index}>
                  <p className="text-sm text-muted-foreground mb-1">{example.description}:</p>
                  <div className="relative">
                    <pre className="bg-secondary p-3 rounded-lg text-sm overflow-x-auto">
                      <code>{example.command}</code>
                    </pre>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="absolute top-1 right-1"
                      onClick={() => copyToClipboard(example.command, `${command.name}-${index}`)}
                    >
                      {copiedCommand === `${command.name}-${index}` ?
                        <Check className="h-3 w-3" /> :
                        <Copy className="h-3 w-3" />
                      }
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Options */}
        {command.options.length > 0 && (
          <div>
            <h4 className="font-semibold mb-2">Options</h4>
            <div className="space-y-1">
              {command.options.map((option: any, index: number) => (
                <div key={index} className="flex items-start gap-3 text-sm">
                  <code className="text-primary whitespace-nowrap">{option.flag}</code>
                  <span className="text-muted-foreground">{option.description}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function ConfigOption({ name, type, default: defaultValue, description }: any) {
  return (
    <div className="flex items-start justify-between p-3 rounded-lg border">
      <div>
        <code className="text-sm font-semibold">{name}</code>
        <Badge variant="outline" className="ml-2 text-xs">{type}</Badge>
        <p className="text-sm text-muted-foreground mt-1">{description}</p>
      </div>
      {defaultValue && (
        <code className="text-sm text-muted-foreground">Default: {defaultValue}</code>
      )}
    </div>
  )
}
