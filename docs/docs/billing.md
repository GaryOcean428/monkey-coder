---
id: billing
title: Billing & Usage
---

# Billing & Usage

Monkey Coder offers flexible pricing tiers to suit different development needs, from individual developers to enterprise teams.

## Pricing Tiers

### Free Tier

Perfect for getting started and small projects:

- ✅ **100 code generations** per month
- ✅ **Basic analysis** features
- ✅ **Community support**
- ✅ **Standard models** access
- ❌ Quantum tasks
- ❌ Priority support
- ❌ Advanced models

### Developer Tier - $29/month

Ideal for active developers and small teams:

- ✅ **1,000 code generations** per month
- ✅ **Advanced analysis** with performance insights
- ✅ **Quantum tasks** (limited)
- ✅ **Premium models** access
- ✅ **Email support**
- ✅ **Custom templates**
- ✅ **API access**

### Team Tier - $99/month

Great for growing teams and projects:

- ✅ **5,000 code generations** per month
- ✅ **Full quantum tasks** suite
- ✅ **All model variants** access
- ✅ **Priority support** (24h response)
- ✅ **Team collaboration** features
- ✅ **Advanced integrations**
- ✅ **Usage analytics**

### Enterprise Tier - Custom Pricing

For large organizations with specific needs:

- ✅ **Unlimited generations**
- ✅ **Custom model training**
- ✅ **On-premise deployment**
- ✅ **24/7 dedicated support**
- ✅ **SLA guarantees**
- ✅ **Security compliance** (SOC2, GDPR)
- ✅ **Custom integrations**

## Usage Tracking

Monitor your usage through the dashboard:

```bash
yarn cli usage --month=current
```

### Key Metrics

- **Code Generations**: Number of AI-generated code snippets
- **Analysis Operations**: Code analysis and review operations
- **Quantum Tasks**: Advanced processing operations
- **API Calls**: Direct API usage
- **Storage**: Code templates and history storage

## Billing API

Integrate billing information into your applications:

```typescript
import { MonkeyCoderBilling } from '@monkey-coder/sdk';

const billing = new MonkeyCoderBilling({
  apiKey: process.env.MONKEY_CODER_API_KEY
});

// Get current usage
const usage = await billing.getCurrentUsage();
console.log('Remaining generations:', usage.remaining);

// Get billing history
const history = await billing.getBillingHistory();
```

## Cost Optimization Tips

1. **Batch Operations**: Group multiple small requests into larger ones
2. **Cache Results**: Store frequently used code patterns locally
3. **Use Templates**: Create reusable templates for common patterns
4. **Monitor Usage**: Set up usage alerts to avoid overages
5. **Optimize Prompts**: Clear, specific prompts generate better results with fewer iterations

## Payment Methods

We accept:
- 💳 Credit/Debit Cards (Visa, MasterCard, American Express)
- 🏦 Bank Transfers (Enterprise only)
- 💰 Cryptocurrency (Bitcoin, Ethereum)
- 📱 Digital Wallets (PayPal, Stripe)

## Billing Support

Need help with billing? Contact our support team:

- **Email**: billing@monkey-coder.dev
- **Chat**: Available in dashboard for paid tiers
- **Phone**: Enterprise customers only

## Fair Usage Policy

To ensure optimal service for all users:

- **Rate Limits**: Prevent excessive API usage
- **Resource Quotas**: Fair allocation of computational resources
- **Quality Standards**: Generated code must meet basic quality thresholds
- **Abuse Prevention**: Automated detection of misuse patterns

## Refund Policy

- **Free Tier**: N/A
- **Developer/Team Tiers**: 30-day money-back guarantee
- **Enterprise**: Custom terms in contract

For questions about refunds or billing disputes, please contact our billing support team.
