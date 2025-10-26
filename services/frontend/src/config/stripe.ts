/**
 * Stripe Configuration for Monkey Coder
 *
 * Product and Price IDs for subscription plans
 * Created via Stripe MCP integration
 */

export const STRIPE_CONFIG = {
  products: {
    basic: {
      id: 'prod_SrDH93yYFjInBe',
      name: 'Monkey Coder Basic',
      description: 'Basic subscription plan for Monkey Coder - Perfect for individual developers and small projects',
      features: [
        '100 API calls per month',
        'Models: GPT-5-nano, Claude-3.5-haiku, Gemini-2.0-flash-lite',
        'Community support',
        'Standard response time',
        'Overage: $0.25 per additional call'
      ],
      limits: {
        apiCalls: 100,
        overagePrice: 0.25
      },
      models: [
        'gpt-5-nano',
        'claude-3-5-haiku-20241022',
        'models/gemini-2.0-flash-lite'
      ]
    },
    pro: {
      id: 'prod_SrDIvsFku9d8VQ',
      name: 'Monkey Coder Pro',
      description: 'Professional subscription plan for Monkey Coder - For teams and growing businesses with advanced features and priority support',
      features: [
        '1,000 API calls per month',
        'Models: GPT-5-mini, GPT-4.1, Claude-sonnet-4, Gemini-2.5-pro',
        'Priority support',
        'Faster response time',
        'Team collaboration (up to 5 users)',
        'Overage: $0.15 per additional call'
      ],
      limits: {
        apiCalls: 1000,
        overagePrice: 0.15
      },
      models: [
        'gpt-5-mini',
        'gpt-4.1',
        'claude-sonnet-4-20250514',
        'gemini-2.5-pro',
        'llama-3.3-70b-versatile',
        'llama-3.1-8b-instant'
      ]
    },
    enterprise: {
      id: 'prod_SrDIQzzTO8gHjX',
      name: 'Monkey Coder Enterprise',
      description: 'Enterprise subscription plan for Monkey Coder - High-volume access with premium models and dedicated support',
      features: [
        '5,000 API calls per month',
        'All premium models: GPT-5, o1, o3, Claude-opus-4.1, Grok-4',
        'Dedicated support with SLA',
        'Custom deployment options',
        'Advanced analytics dashboard',
        'SSO integration',
        'Bulk overage packages available',
        'Overage: $0.10 per additional call'
      ],
      limits: {
        apiCalls: 5000,
        overagePrice: 0.10
      },
      models: [
        'gpt-5',
        'o1',
        'o3',
        'o3-pro',
        'gpt-4.1',
        'claude-opus-4-1-20250805',
        'claude-opus-4-20250514',
        'claude-sonnet-4-20250514',
        'grok-4-latest',
        'gemini-2.5-pro',
        'llama-3.3-70b-versatile',
        'moonshotai/kimi-k2-instruct'
      ]
    }
  },
  prices: {
    basic: {
      // Note: These are one-time prices. Need to create recurring subscription prices via Stripe Dashboard
      oneTime: 'price_1RvUtYAYIAu3GrrMKHZI181x', // $19 one-time
      monthly: '', // To be created via Stripe Dashboard - $19/month recurring
      annual: '' // To be created via Stripe Dashboard
    },
    pro: {
      monthly: '', // To be created via Stripe Dashboard - $49/month recurring
      annual: '' // To be created via Stripe Dashboard
    },
    enterprise: {
      monthly: '', // To be created via Stripe Dashboard - $199/month recurring
      annual: '' // To be created via Stripe Dashboard
    }
  },
  // Stripe public key (safe to expose in frontend)
  publicKey: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '',

  // Webhook endpoints
  webhooks: {
    paymentSuccess: '/api/stripe/webhook/payment-success',
    subscriptionUpdate: '/api/stripe/webhook/subscription-update',
    paymentFailed: '/api/stripe/webhook/payment-failed'
  }
};

export const PRICING_TIERS = [
  {
    name: 'Basic',
    productId: STRIPE_CONFIG.products.basic.id,
    price: 19,
    currency: 'USD',
    period: 'month' as const,
    features: STRIPE_CONFIG.products.basic.features,
    highlighted: false
  },
  {
    name: 'Pro',
    productId: STRIPE_CONFIG.products.pro.id,
    price: 49,
    currency: 'USD',
    period: 'month' as const,
    features: STRIPE_CONFIG.products.pro.features,
    highlighted: true,
    badge: 'Most Popular'
  },
  {
    name: 'Enterprise',
    productId: STRIPE_CONFIG.products.enterprise.id,
    price: 199,
    currency: 'USD',
    period: 'month' as const,
    features: STRIPE_CONFIG.products.enterprise.features,
    highlighted: false
  }
];
