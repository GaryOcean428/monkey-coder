import { Button } from '@/components/ui/button'
import { Code2, Zap, Shield, ArrowRight, Github, Twitter } from 'lucide-react'
import Link from 'next/link'
import { Hero } from '@/components/marketing/hero'
import { Features } from '@/components/marketing/features'
import { PricingSection } from '@/components/marketing/pricing'
import { Footer } from '@/components/marketing/footer'
import { Header } from '@/components/marketing/header'

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="flex-1">
        {/* Hero Section */}
        <Hero />

        {/* Features Section */}
        <Features />

        {/* Pricing Section */}
        <PricingSection />

        {/* CTA Section */}
        <section className="border-t bg-gradient-to-r from-primary/10 via-primary/5 to-primary/10 neon-divider">
          <div className="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                Ready to accelerate your development?
              </h2>
              <p className="mx-auto mt-6 max-w-xl text-lg leading-8 text-muted-foreground">
                Join thousands of developers using Monkey Coder to build better software faster.
              </p>
              <div className="mt-10 flex items-center justify-center gap-x-6">
                <Link href="/signup">
                  <Button size="lg" className="gap-2">
                    Get started for free
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/pricing">
                  <Button variant="outline" size="lg">
                    View pricing
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Stats Section */}
        <section className="bg-primary/5 py-24 sm:py-32">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                Building the Future of Development
              </h2>
              <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
                Join us on our journey to revolutionize how developers build software.
              </p>
            </div>
            <dl className="grid grid-cols-1 gap-x-8 gap-y-16 text-center lg:grid-cols-3">
              <div className="mx-auto flex max-w-xs flex-col gap-y-4">
                <dt className="text-base leading-7 text-muted-foreground">
                  AI Models Supported
                </dt>
                <dd className="order-first text-3xl font-semibold tracking-tight sm:text-5xl">
                  5+
                </dd>
              </div>
              <div className="mx-auto flex max-w-xs flex-col gap-y-4">
                <dt className="text-base leading-7 text-muted-foreground">
                  Code Generation
                </dt>
                <dd className="order-first text-3xl font-semibold tracking-tight sm:text-5xl">
                  AI-Powered
                </dd>
              </div>
              <div className="mx-auto flex max-w-xs flex-col gap-y-4">
                <dt className="text-base leading-7 text-muted-foreground">
                  Development Speed
                </dt>
                <dd className="order-first text-3xl font-semibold tracking-tight sm:text-5xl">
                  10x
                </dd>
              </div>
            </dl>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}
