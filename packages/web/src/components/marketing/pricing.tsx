import { Check } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const tiers = [
  {
    name: 'Hobby',
    id: 'tier-hobby',
    href: '/signup',
    priceMonthly: '$0',
    description: 'Perfect for side projects and learning.',
    features: [
      '1,000 code generations per month',
      'Basic code analysis',
      'Community support',
      'Access to standard models',
      'Export to GitHub',
    ],
    mostPopular: false,
  },
  {
    name: 'Pro',
    id: 'tier-pro',
    href: '/signup',
    priceMonthly: '$29',
    description: 'For professional developers and small teams.',
    features: [
      'Unlimited code generations',
      'Advanced code analysis',
      'Priority email support',
      'Access to all AI models',
      'Team collaboration (up to 5)',
      'Custom model fine-tuning',
      'API access',
      'Export to any platform',
    ],
    mostPopular: true,
  },
  {
    name: 'Enterprise',
    id: 'tier-enterprise',
    href: '/contact',
    priceMonthly: 'Custom',
    description: 'Dedicated support and infrastructure for your company.',
    features: [
      'Everything in Pro',
      'Unlimited team members',
      'SSO/SAML authentication',
      'Dedicated account manager',
      'Custom AI model training',
      'On-premise deployment option',
      'SLA guarantee',
      'Advanced security features',
    ],
    mostPopular: false,
  },
]

export function PricingSection() {
  return (
    <section className="bg-primary/5 py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="text-base font-semibold leading-7 text-primary">Pricing</h2>
          <p className="mt-2 text-4xl font-bold tracking-tight sm:text-5xl">
            Choose the right plan for you
          </p>
        </div>
        <p className="mx-auto mt-6 max-w-2xl text-center text-lg leading-8 text-muted-foreground">
          Start free and upgrade as you grow. All plans include core features with no hidden fees.
        </p>
        <div className="isolate mx-auto mt-16 grid max-w-md grid-cols-1 gap-y-8 sm:mt-20 lg:mx-0 lg:max-w-none lg:grid-cols-3">
          {tiers.map((tier, tierIdx) => (
            <div
              key={tier.id}
              className={cn(
                tier.mostPopular ? 'lg:z-10 lg:rounded-b-none' : 'lg:mt-8',
                tierIdx === 0 ? 'lg:rounded-r-none' : '',
                tierIdx === tiers.length - 1 ? 'lg:rounded-l-none' : '',
                'flex flex-col justify-between rounded-3xl bg-white p-8 ring-1 ring-gray-200 xl:p-10 dark:bg-gray-900 dark:ring-gray-800'
              )}
            >
              <div>
                <div className="flex items-center justify-between gap-x-4">
                  <h3
                    id={tier.id}
                    className={cn(
                      tier.mostPopular ? 'text-primary' : 'text-gray-900 dark:text-gray-100',
                      'text-lg font-semibold leading-8'
                    )}
                  >
                    {tier.name}
                  </h3>
                  {tier.mostPopular ? (
                    <p className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-semibold leading-5 text-primary">
                      Most popular
                    </p>
                  ) : null}
                </div>
                <p className="mt-4 text-sm leading-6 text-gray-600 dark:text-gray-400">
                  {tier.description}
                </p>
                <p className="mt-6 flex items-baseline gap-x-1">
                  <span className="text-4xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
                    {tier.priceMonthly}
                  </span>
                  {tier.priceMonthly !== 'Custom' && (
                    <span className="text-sm font-semibold leading-6 text-gray-600 dark:text-gray-400">
                      /month
                    </span>
                  )}
                </p>
                <ul role="list" className="mt-8 space-y-3 text-sm leading-6 text-gray-600 dark:text-gray-400">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex gap-x-3">
                      <Check className="h-6 w-5 flex-none text-primary" aria-hidden="true" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
              <Link href={tier.href} className="mt-8">
                <Button
                  className="w-full"
                  variant={tier.mostPopular ? 'default' : 'outline'}
                  size="lg"
                >
                  {tier.name === 'Enterprise' ? 'Contact sales' : 'Get started'}
                </Button>
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
