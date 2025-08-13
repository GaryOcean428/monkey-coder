'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckIcon } from 'lucide-react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface PricingCardProps {
  name: string;
  description: string;
  price: number;
  currency: string;
  period: 'month' | 'year';
  features: string[];
  highlighted?: boolean;
  badge?: string;
  productId: string;
  priceId?: string;
}

export function PricingCard({
  name,
  description,
  price,
  currency,
  period,
  features,
  highlighted = false,
  badge,
  productId,
  priceId,
}: PricingCardProps) {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubscribe = async () => {
    setLoading(true);
    try {
      // Here we'll call our API to create a checkout session
      const response = await fetch('/api/stripe/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          productId,
          priceId,
          successUrl: `${window.location.origin}/dashboard?session_id={CHECKOUT_SESSION_ID}`,
          cancelUrl: `${window.location.origin}/pricing`,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create checkout session');
      }

      const { sessionUrl } = await response.json();

      // Redirect to Stripe Checkout
      if (sessionUrl) {
        window.location.href = sessionUrl;
      }
    } catch (error) {
      console.error('Error creating checkout session:', error);
      // TODO: Show error toast
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className={highlighted ? 'border-cyan-500 border-2 shadow-lg relative' : 'relative'}>
      {badge && (
        <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-cyan-500 text-white">
          {badge}
        </Badge>
      )}

      <CardHeader>
        <CardTitle className="text-2xl">{name}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="text-4xl font-bold">
          <span className="text-sm font-normal align-top">{currency === 'USD' ? '$' : currency}</span>
          {price}
          <span className="text-sm font-normal text-muted-foreground">/{period}</span>
        </div>

        <ul className="space-y-2">
          {features.map((feature, index) => (
            <li key={index} className="flex items-start gap-2">
              <CheckIcon className="h-5 w-5 text-cyan-500 mt-0.5 shrink-0" />
              <span className="text-sm">{feature}</span>
            </li>
          ))}
        </ul>
      </CardContent>

      <CardFooter>
        <Button
          onClick={handleSubscribe}
          disabled={loading}
          className={highlighted ? 'w-full bg-cyan-500 hover:bg-cyan-600' : 'w-full'}
        >
          {loading ? 'Processing...' : 'Get Started'}
        </Button>
      </CardFooter>
    </Card>
  );
}
