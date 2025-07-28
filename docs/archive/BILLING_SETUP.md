# Usage Metering & Billing System

This document describes the usage metering and billing system implemented for the Monkey Coder Core API.

## Overview

The billing system provides:

1. **PostgreSQL Database**: `usage_events` table for tracking API usage
2. **Automatic Usage Tracking**: Middleware records tokens × model price
3. **Stripe Integration**: Metered billing with customer management
4. **Daily Reporting**: GitHub Actions cron job reports usage to Stripe
5. **Billing Portal**: `/v1/billing/portal` endpoint for customer billing management

## Components

### 1. Database Schema

#### `usage_events` Table
- `id`: Unique event identifier
- `api_key_hash`: Hashed API key for privacy
- `execution_id`: Links to task execution
- `task_type`: Type of task executed
- `tokens_input`, `tokens_output`, `tokens_total`: Token usage
- `provider`, `model`: AI provider and model used
- `model_cost_input`, `model_cost_output`: Pricing per token
- `cost_input`, `cost_output`, `cost_total`: Calculated costs
- `execution_time`: Task execution time
- `status`: Execution status
- `created_at`: Timestamp
- `metadata`: Additional JSON metadata

#### `billing_customers` Table
- `id`: Unique customer identifier
- `api_key_hash`: Links to usage events
- `stripe_customer_id`: Stripe customer ID
- `email`, `name`, `company`: Customer info
- `billing_interval`: Billing frequency
- `is_active`: Customer status

### 2. Pricing System

#### Model Pricing Data
Located in `packages/core/monkey_coder/pricing/models.py`:

- Comprehensive pricing for all supported models
- Updated nightly via cron job
- Per-token pricing (not per 1K tokens) for accuracy

#### Pricing Middleware
- Automatically tracks usage for `/v1/execute` endpoints
- Records detailed usage events with cost calculations
- Extracts pricing information from model pricing data
- Handles errors gracefully without failing requests

### 3. Stripe Integration

#### Customer Management
- Create customers via API key
- Link API keys to Stripe customer IDs
- Store customer information in database

#### Metered Billing
- Daily cron job aggregates usage by customer
- Reports usage to Stripe subscription items
- Handles billing intervals and pricing tiers

#### Billing Portal
- `/v1/billing/portal` endpoint
- Creates Stripe billing portal sessions
- Allows customers to manage payment methods and view invoices

### 4. Daily Cron Job

#### GitHub Actions Workflow
Located in `.github/workflows/daily-billing-report.yml`:

- Runs daily at 2:00 AM UTC
- Reports previous day's usage to Stripe
- Updates model pricing data
- Cleans up old usage events (weekly)
- Automatic error notification via GitHub Issues

## Setup Instructions

### 1. Environment Variables

Add to your Railway/deployment environment:

```bash
DATABASE_URL=postgresql://...          # PostgreSQL connection
STRIPE_API_KEY=sk_live_...            # Stripe secret key
ENABLE_PRICING_MIDDLEWARE=true         # Enable usage tracking
```

### 2. Database Setup

The database tables are created automatically via migrations on application startup. No manual setup required.

### 3. Stripe Configuration

1. Create a Stripe account
2. Set up products and pricing plans for metered billing
3. Configure webhooks (if needed)
4. Add your Stripe API key to environment variables

### 4. GitHub Secrets

For the daily cron job, add these secrets to your GitHub repository:

- `DATABASE_URL`: PostgreSQL connection string
- `STRIPE_API_KEY`: Stripe secret key

### 5. Customer Onboarding

To set up billing for a customer:

```python
from monkey_coder.database.models import BillingCustomer
from monkey_coder.billing import create_stripe_customer

# Create Stripe customer
stripe_customer_id = create_stripe_customer(
    email="customer@example.com",
    name="Customer Name", 
    api_key_hash="hashed_api_key"
)

# Create billing customer record
await BillingCustomer.create(
    api_key_hash="hashed_api_key",
    stripe_customer_id=stripe_customer_id,
    email="customer@example.com",
    name="Customer Name"
)
```

## API Endpoints

### Usage Metrics
```http
GET /v1/billing/usage?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer YOUR_API_KEY
```

### Billing Portal
```http
POST /v1/billing/portal
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "return_url": "https://yourdomain.com/billing"
}
```

## Monitoring

### Usage Tracking
- All API requests to `/v1/execute` are automatically tracked
- Usage data is stored in PostgreSQL with detailed breakdowns
- Pricing is calculated in real-time using current model rates

### Error Handling
- Middleware handles errors gracefully
- Failed usage tracking doesn't break API requests
- Automatic GitHub Issue creation for cron job failures

### Data Retention
- Usage events are kept for 90 days by default
- Automatic cleanup via weekly cron job
- Configurable retention period

## Security

### API Key Privacy
- API keys are hashed using SHA-256
- Only hashed versions are stored in database
- Original API keys never logged or persisted

### Data Protection
- All usage data is encrypted at rest (PostgreSQL)
- Secure connection to Stripe API
- Environment variables for sensitive configuration

## Scaling Considerations

### Database Performance
- Indexed queries on `api_key_hash` and `created_at`
- Batch processing for large usage datasets
- Automatic cleanup of old data

### Stripe Rate Limits
- Daily batching of usage reports
- Error handling and retry logic
- Graceful degradation on API failures

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check `DATABASE_URL` environment variable
   - Verify PostgreSQL instance is running
   - Check network connectivity

2. **Stripe API Errors**
   - Verify `STRIPE_API_KEY` is correct
   - Check Stripe account status
   - Review Stripe dashboard for issues

3. **Missing Usage Data**
   - Verify `ENABLE_PRICING_MIDDLEWARE=true`
   - Check application logs for middleware errors
   - Ensure pricing data is loaded

4. **Cron Job Failures**
   - Check GitHub Actions logs
   - Verify repository secrets are set
   - Review database connectivity from GitHub Actions

### Debugging

Enable debug logging:
```python
import logging
logging.getLogger("monkey_coder.billing").setLevel(logging.DEBUG)
logging.getLogger("monkey_coder.pricing").setLevel(logging.DEBUG)
```

## Future Enhancements

1. **Real-time Usage Alerts**
   - Webhook notifications for usage thresholds
   - Rate limiting based on usage quotas

2. **Advanced Analytics**
   - Usage trend analysis
   - Cost optimization recommendations
   - Provider performance metrics

3. **Multi-tier Pricing**
   - Volume discounts
   - Enterprise pricing tiers
   - Custom pricing models

4. **Enhanced Reporting**
   - Customer usage dashboards
   - Detailed cost breakdowns
   - Export capabilities
