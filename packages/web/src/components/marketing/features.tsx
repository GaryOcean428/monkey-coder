import { Code2, Zap, Shield, Brain, Layers, Globe, GitBranch, Sparkles } from 'lucide-react'

const features = [
  {
    name: 'Multi-Language Support',
    description: 'Generate code in multiple programming languages from Python to Rust, JavaScript to Go.',
    icon: Globe,
  },
  {
    name: 'AI-Powered Intelligence',
    description: 'Leverages advanced language models to understand context and generate optimal solutions.',
    icon: Brain,
  },
  {
    name: 'Lightning Fast',
    description: 'Get production-ready code in seconds, not hours. Focus on what matters most.',
    icon: Zap,
  },
  {
    name: 'Security First',
    description: 'Generated code follows security best practices and industry standards.',
    icon: Shield,
  },
  {
    name: 'Framework Aware',
    description: 'Understands popular frameworks like React, Django, Express, and generates idiomatic code.',
    icon: Layers,
  },
  {
    name: 'Version Control Ready',
    description: 'Clean, well-documented code that integrates seamlessly with your Git workflow.',
    icon: GitBranch,
  },
  {
    name: 'Code Analysis',
    description: 'Analyze existing code for bugs, performance issues, and security vulnerabilities.',
    icon: Code2,
  },
  {
    name: 'Continuous Learning',
    description: 'Models are regularly updated with the latest programming patterns and best practices.',
    icon: Sparkles,
  },
]

export function Features() {
  return (
    <section className="py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-base font-semibold leading-7 text-primary">Everything you need</h2>
          <p className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
            Powerful features for modern development
          </p>
          <p className="mt-6 text-lg leading-8 text-muted-foreground">
            Monkey Coder provides all the tools you need to accelerate your development workflow
            and build better software faster.
          </p>
        </div>
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-4">
            {features.map((feature) => (
              <div key={feature.name} className="flex flex-col neon-card p-4 rounded-lg">
                <dt className="flex items-center gap-x-3 text-base font-semibold leading-7">
                  <feature.icon className="h-5 w-5 flex-none text-primary neon-text-cyan" aria-hidden="true" />
                  {feature.name}
                </dt>
                <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-muted-foreground">
                  <p className="flex-auto">{feature.description}</p>
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </section>
  )
}
