import { PricingSection } from '@/components/marketing/pricing'
import { Footer } from '@/components/marketing/footer'
import { Header } from '@/components/marketing/header'

export default function PricingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="flex-1">
        {/* Page Header */}
        <div className="bg-gradient-to-b from-background to-secondary/10 py-16">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
                Simple, transparent pricing
              </h1>
              <p className="mt-6 text-lg leading-8 text-muted-foreground">
                Choose the perfect plan for your needs. Always flexible to scale up or down.
              </p>
            </div>
          </div>
        </div>

        {/* Pricing Section Component */}
        <PricingSection />

        {/* FAQ Section */}
        <section className="py-24 sm:py-32">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <div className="mx-auto max-w-2xl lg:text-center">
              <h2 className="text-base font-semibold leading-7 text-primary">FAQ</h2>
              <p className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
                Frequently asked questions
              </p>
            </div>
            <div className="mx-auto mt-16 max-w-2xl">
              <dl className="space-y-8">
                <div>
                  <dt className="text-lg font-semibold">Can I change my plan later?</dt>
                  <dd className="mt-2 text-base text-muted-foreground">
                    Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.
                  </dd>
                </div>
                <div>
                  <dt className="text-lg font-semibold">Is there a free trial?</dt>
                  <dd className="mt-2 text-base text-muted-foreground">
                    Yes, all paid plans come with a 14-day free trial. No credit card required.
                  </dd>
                </div>
                <div>
                  <dt className="text-lg font-semibold">What payment methods do you accept?</dt>
                  <dd className="mt-2 text-base text-muted-foreground">
                    We accept all major credit cards, PayPal, and wire transfers for enterprise customers.
                  </dd>
                </div>
                <div>
                  <dt className="text-lg font-semibold">Can I cancel my subscription?</dt>
                  <dd className="mt-2 text-base text-muted-foreground">
                    Yes, you can cancel your subscription at any time. You'll continue to have access until the end of your billing period.
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}
