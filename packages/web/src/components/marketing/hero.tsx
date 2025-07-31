import Link from 'next/link'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { ArrowRight, Code2, Sparkles, Zap } from 'lucide-react'

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-background to-primary/5">
      <div className="absolute inset-0 bg-grid-black/[0.02] -z-10" />
      <div className="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8 lg:py-40">
        <div className="mx-auto max-w-4xl text-center">
          {/* Large Hero Logo */}
          <div className="mb-12 flex justify-center animate-fade-up">
            <div className="relative">
              <Image
                src="/splash.png"
                alt="Monkey Coder"
                width={400}
                height={107}
                className="h-32 w-auto drop-shadow-2xl neon-logo"
                priority
              />
              <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-transparent rounded-lg blur-xl -z-10" />
            </div>
          </div>

          <div className="mb-8 flex justify-center animate-fade-up animation-delay-100">
            <div className="relative rounded-full px-3 py-1 text-sm leading-6 text-muted-foreground ring-1 ring-gray-900/10 hover:ring-gray-900/20 dark:ring-gray-100/10 dark:hover:ring-gray-100/20">
              Powered by state-of-the-art AI models{' '}
              <Link href="/docs" className="font-semibold text-primary">
                <span className="absolute inset-0" aria-hidden="true" />
                Learn more <span aria-hidden="true">&rarr;</span>
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
            Monkey Coder uses advanced AI to generate, analyze, and optimize code across multiple programming languages.
            Build faster, ship better, and let AI handle the repetitive tasks.
          </p>

          <div className="mt-10 flex items-center justify-center gap-x-6 animate-fade-up animation-delay-200">
            <Link href="/signup">
              <Button size="lg" className="gap-2 neon-button-cyan">
                Start coding for free
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="#demo">
              <Button variant="outline" size="lg" className="neon-button-cyan">
                Watch demo
              </Button>
            </Link>
          </div>

          <div className="mt-10 flex items-center justify-center gap-x-8 text-sm text-muted-foreground animate-fade-up animation-delay-300">
            <div className="flex items-center gap-2">
              <Code2 className="h-4 w-4" />
              <span>Multi-language</span>
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

        {/* Code Preview */}
        <div className="mt-16 flow-root sm:mt-24">
          <div className="relative rounded-xl bg-gray-900/5 p-2 ring-1 ring-inset ring-gray-900/10 lg:-m-4 lg:rounded-2xl lg:p-4">
            <div className="rounded-md bg-gray-900 p-4 text-sm text-gray-300 shadow-2xl ring-1 ring-white/10">
              <pre className="overflow-x-auto">
                <code>{`// Generate a REST API endpoint
const prompt = "Create a user authentication endpoint with JWT"
const result = await monkeyCoder.generate({
  prompt,
  language: "typescript",
  framework: "express"
})

// AI generates production-ready code with best practices
app.post('/api/auth/login', async (req, res) => {
  // Secure, tested, and optimized implementation
})`}</code>
              </pre>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
