'use client';

import { PricingCard } from '@/components/pricing-card';
import { PRICING_TIERS } from '@/config/stripe';

export default function PricingPage() {
  return (
    <div className="container mx-auto py-16 px-4">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">Choose Your Plan</h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Select the perfect plan for your needs. All plans include access to our AI-powered coding assistant
          with different levels of features and support.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
        {PRICING_TIERS.map((tier) => (
          <PricingCard
            key={tier.name}
            name={tier.name}
            description={`${tier.name} subscription plan`}
            price={tier.price}
            currency={tier.currency}
            period={tier.period}
            features={tier.features}
            highlighted={tier.highlighted}
            badge={tier.badge}
            productId={tier.productId}
          />
        ))}
      </div>

      <div className="mt-16 text-center">
        <p className="text-sm text-muted-foreground">
          All plans are billed monthly. Cancel anytime.
        </p>
        <p className="text-sm text-muted-foreground mt-2">
          Need a custom solution? <a href="/contact" className="text-cyan-500 hover:underline">Contact us</a>
        </p>
      </div>
    </div>
  );
}
