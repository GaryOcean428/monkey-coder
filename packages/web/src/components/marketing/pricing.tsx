"use client"

import { Check, Calculator, Info } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { useState } from 'react'

// Model costs with 15% markup (10% GST + 5% profit) applied
// Base costs from MODELS_MANIFEST.md × 1.15
const modelCosts = {
  // Budget tier
  'gpt-4.1-mini': {
    input: 0.00014, // $0.00012 × 1.15
    output: 0.00055, // $0.00048 × 1.15
    display: 'GPT-4.1 Mini'
  },
  'gemini-2.5-flash-lite': {
    input: 0.00002, // $0.00001875 × 1.15
    output: 0.00009, // $0.000075 × 1.15
    display: 'Gemini 2.5 Flash Lite'
  },
  'claude-3-5-haiku': {
    input: 0.00092, // $0.0008 × 1.15
    output: 0.00460, // $0.004 × 1.15
    display: 'Claude 3.5 Haiku'
  },

  // Balanced tier
  'gpt-4.1': {
    input: 0.00230, // $0.002 × 1.15
    output: 0.00920, // $0.008 × 1.15
    display: 'GPT-4.1'
  },
  'claude-3-5-sonnet': {
    input: 0.00345, // $0.003 × 1.15
    output: 0.01725, // $0.015 × 1.15
    display: 'Claude 3.5 Sonnet'
  },
  'gemini-2.5-flash': {
    input: 0.00009, // $0.000075 × 1.15
    output: 0.00035, // $0.0003 × 1.15
    display: 'Gemini 2.5 Flash'
  },
  'o4-mini': {
    input: 0.00127, // $0.0011 × 1.15
    output: 0.00506, // $0.0044 × 1.15
    display: 'O4 Mini'
  },

  // Premium tier
  'claude-opus-4-1': {
    input: 0.01725, // $0.015 × 1.15
    output: 0.08625, // $0.075 × 1.15
    display: 'Claude Opus 4.1'
  },
  'o3-pro': {
    input: 0.02300, // $0.020 × 1.15
    output: 0.09200, // $0.080 × 1.15
    display: 'O3 Pro'
  },
  'gemini-2.5-pro': {
    input: 0.00144, // $0.00125 × 1.15
    output: 0.00575, // $0.005 × 1.15
    display: 'Gemini 2.5 Pro'
  },
  'o3': {
    input: 0.00230, // $0.002 × 1.15
    output: 0.00920, // $0.008 × 1.15
    display: 'O3'
  }
}

const tiers = [
  {
    name: 'Free',
    id: 'tier-free',
    href: '/signup',
    priceMonthly: '$0',
    priceAUD: '$0 AUD',
    description: 'Get started with AI code generation.',
    features: [
      '50 code generations per month',
      'Basic models (Gemini 2.5 Flash Lite)',
      'Community support',
      'Export to GitHub',
      'Basic code analysis',
    ],
    usage: 'Included: 50 generations',
    gstNote: '',
    mostPopular: false,
  },
  {
    name: 'Starter',
    id: 'tier-starter',
    href: '/signup',
    priceMonthly: 'Pay as you go',
    priceAUD: 'Usage-based',
    description: 'Flexible pricing for growing projects.',
    features: [
      'Pay per generation',
      'Access to all standard models',
      'Email support',
      'API access (rate limited)',
      'Export to any platform',
      'Usage analytics dashboard',
      'Model selection control',
    ],
    usage: 'From $0.00002 per generation',
    gstNote: 'All prices include 10% GST',
    mostPopular: false,
  },
  {
    name: 'Pro',
    id: 'tier-pro',
    href: '/signup',
    priceMonthly: '$79',
    priceAUD: '$118.50 AUD',
    description: 'For professional developers and teams.',
    features: [
      '2,000 included generations/month',
      'Then $0.025 per generation',
      'Access to all AI models',
      'Priority support',
      'Team collaboration (up to 10)',
      'Advanced code analysis',
      'Custom model preferences',
      'Unlimited API access',
      'Advanced analytics',
    ],
    usage: '2,000 generations included',
    gstNote: 'All prices include 10% GST',
    mostPopular: true,
  },
  {
    name: 'Enterprise',
    id: 'tier-enterprise',
    href: '/contact',
    priceMonthly: 'Custom',
    priceAUD: 'Contact sales',
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
      'Volume discounts',
      'Custom billing',
    ],
    usage: 'Volume-based pricing',
    gstNote: 'Custom GST handling available',
    mostPopular: false,
  },
]

export function PricingSection() {
  const [showCalculator, setShowCalculator] = useState(false)
  const [selectedModel, setSelectedModel] = useState('gpt-4.1')
  const [tokensInput, setTokensInput] = useState(1000)
  const [tokensOutput, setTokensOutput] = useState(1000)

  const calculateCost = () => {
    const model = modelCosts[selectedModel as keyof typeof modelCosts]
    if (!model) return { usd: 0, aud: 0 }

    const inputCost = (tokensInput / 1000) * model.input
    const outputCost = (tokensOutput / 1000) * model.output
    const totalUSD = inputCost + outputCost
    const totalAUD = totalUSD * 1.5 // Approximate USD to AUD conversion

    return {
      usd: totalUSD.toFixed(4),
      aud: totalAUD.toFixed(4)
    }
  }

  const cost = calculateCost()

  return (
    <section className="bg-gradient-to-b from-background to-secondary/5 py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="text-base font-semibold leading-7 text-primary">Pricing</h2>
          <p className="mt-2 text-4xl font-bold tracking-tight sm:text-5xl">
            Transparent usage-based pricing
          </p>
        </div>
        <p className="mx-auto mt-6 max-w-2xl text-center text-lg leading-8 text-muted-foreground">
          Start free and upgrade as you grow. All prices include 10% GST for Australian customers plus our 5% platform fee.
        </p>

        {/* Pricing Calculator Toggle */}
        <div className="mx-auto mt-8 text-center">
          <Button
            variant="outline"
            onClick={() => setShowCalculator(!showCalculator)}
            className="gap-2"
          >
            <Calculator className="h-4 w-4" />
            {showCalculator ? 'Hide' : 'Show'} Pricing Calculator
          </Button>
        </div>

        {/* Pricing Calculator */}
        {showCalculator && (
          <div className="mx-auto mt-8 max-w-2xl rounded-lg border bg-card p-6">
            <h3 className="text-lg font-semibold mb-4">Usage Cost Calculator</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Select Model</label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full rounded-md border border-input bg-background px-3 py-2"
                >
                  <optgroup label="Budget Tier">
                    <option value="gpt-4.1-mini">GPT-4.1 Mini</option>
                    <option value="gemini-2.5-flash-lite">Gemini 2.5 Flash Lite</option>
                    <option value="claude-3-5-haiku">Claude 3.5 Haiku</option>
                  </optgroup>
                  <optgroup label="Balanced Tier">
                    <option value="gpt-4.1">GPT-4.1</option>
                    <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                    <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                    <option value="o4-mini">O4 Mini (Reasoning)</option>
                  </optgroup>
                  <optgroup label="Premium Tier">
                    <option value="claude-opus-4-1">Claude Opus 4.1</option>
                    <option value="o3-pro">O3 Pro (Advanced Reasoning)</option>
                    <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                    <option value="o3">O3 (Reasoning)</option>
                  </optgroup>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Input Tokens</label>
                  <input
                    type="number"
                    value={tokensInput}
                    onChange={(e) => setTokensInput(Number(e.target.value))}
                    className="w-full rounded-md border border-input bg-background px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Output Tokens</label>
                  <input
                    type="number"
                    value={tokensOutput}
                    onChange={(e) => setTokensOutput(Number(e.target.value))}
                    className="w-full rounded-md border border-input bg-background px-3 py-2"
                  />
                </div>
              </div>

              <div className="rounded-lg bg-secondary/50 p-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Estimated Cost:</span>
                  <div className="text-right">
                    <div className="text-lg font-semibold">${cost.usd} USD</div>
                    <div className="text-sm text-muted-foreground">${cost.aud} AUD</div>
                  </div>
                </div>
                <div className="mt-2 flex items-center gap-1 text-xs text-muted-foreground">
                  <Info className="h-3 w-3" />
                  <span>Includes 10% GST + 5% platform fee</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Pricing Tiers */}
        <div className="isolate mx-auto mt-16 grid max-w-md grid-cols-1 gap-y-8 sm:mt-20 lg:mx-0 lg:max-w-none lg:grid-cols-4">
          {tiers.map((tier, tierIdx) => (
            <div
              key={tier.id}
              className={cn(
                tier.mostPopular ? 'lg:z-10 ring-2 ring-primary' : 'lg:mt-8',
                tierIdx === 0 ? 'lg:rounded-r-none' : '',
                tierIdx === tiers.length - 1 ? 'lg:rounded-l-none' : '',
                'flex flex-col justify-between rounded-3xl bg-card p-8 ring-1 ring-border xl:p-10'
              )}
            >
              <div>
                <div className="flex items-center justify-between gap-x-4">
                  <h3
                    id={tier.id}
                    className={cn(
                      tier.mostPopular ? 'text-primary' : '',
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
                <p className="mt-4 text-sm leading-6 text-muted-foreground">
                  {tier.description}
                </p>
                <p className="mt-6 flex items-baseline gap-x-1">
                  <span className="text-4xl font-bold tracking-tight">
                    {tier.priceMonthly}
                  </span>
                  {tier.priceMonthly !== 'Custom' && tier.priceMonthly !== 'Pay as you go' && (
                    <span className="text-sm font-semibold leading-6 text-muted-foreground">
                      /month
                    </span>
                  )}
                </p>
                {tier.priceAUD !== tier.priceMonthly && (
                  <p className="text-sm text-muted-foreground mt-1">
                    {tier.priceAUD}
                  </p>
                )}
                {tier.usage && (
                  <p className="mt-2 text-xs font-medium text-primary">
                    {tier.usage}
                  </p>
                )}
                {tier.gstNote && (
                  <p className="mt-1 text-xs text-muted-foreground italic">
                    {tier.gstNote}
                  </p>
                )}
                <ul role="list" className="mt-8 space-y-3 text-sm leading-6 text-muted-foreground">
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

        {/* Model Comparison Table */}
        <div className="mx-auto mt-16 max-w-7xl">
          <h3 className="text-2xl font-bold text-center mb-8">Available Models & Pricing</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border">
              <thead>
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Model</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Best For</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Input (per 1K tokens)</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Output (per 1K tokens)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                <tr className="bg-secondary/20">
                  <td colSpan={4} className="px-6 py-2 text-sm font-semibold">Budget Tier</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm">GPT-4.1 Mini</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">Quick tasks, simple code</td>
                  <td className="px-6 py-4 text-sm">${modelCosts['gpt-4.1-mini'].input.toFixed(5)}</td>
                  <td className="px-6 py-4 text-sm">${modelCosts['gpt-4.1-mini'].output.toFixed(5)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm">Gemini 2.5 Flash Lite</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">High volume, cost-critical</td>
                  <td className="px-6 py-4 text-sm">${modelCosts['gemini-2.5-flash-lite'].input.toFixed(5)}</td>
                  <td className="px-6 py-4 text-sm">${modelCosts['gemini-2.5-flash-lite'].output.toFixed(5)}</td>
                </tr>
                <tr className="bg-secondary/20">
                  <td colSpan={4} className="px-6 py-2 text-sm font-semibold">Balanced Tier</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm">GPT-4.1</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">General coding, complex tasks</td>
                  <td className="px-6 py-4 text-sm">${modelCosts['gpt-4.1'].input.toFixed(5)}</td>
                  <td className="px-6 py-4 text-sm">${modelCosts['gpt-4.1'].output.toFixed(5)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm">Claude 3.5 Sonnet</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">Complex reasoning, analysis</td>
                  <td className="px-6 py-4 text-sm">${modelCosts['claude-3-5-sonnet'].input.toFixed(5)}</td>
                  <td className="px-6 py-4 text-sm">${modelCosts['claude-3-5-sonnet'].output.toFixed(5)}</td>
                </tr>
                <tr className="bg-secondary/20">
                  <td colSpan={4} className="px-6 py-2 text-sm font-semibold">Premium Tier</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm">Claude Opus 4.1</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">Most complex tasks, superior reasoning</td>
                  <td className="px-6 py-4 text-sm">${modelCosts['claude-opus-4-1'].input.toFixed(5)}</td>
                  <td className="px-6 py-4 text-sm">${modelCosts['claude-opus-4-1'].output.toFixed(5)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-sm">O3 Pro</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">Advanced reasoning, scientific analysis</td>
                  <td className="px-6 py-4 text-sm">${modelCosts['o3-pro'].input.toFixed(5)}</td>
                  <td className="px-6 py-4 text-sm">${modelCosts['o3-pro'].output.toFixed(5)}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div className="mt-4 text-center">
            <p className="text-xs text-muted-foreground">
              All prices include 10% GST and 5% platform fee. Prices in USD. AUD conversion approximate.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
