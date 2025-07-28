# Railway Sentry Configuration

## Required Environment Variables

Add these environment variables to your Railway service to enable Sentry error tracking:

### Essential Variables

1. **SENTRY_DSN**
   - Description: Your Sentry project's DSN (Data Source Name)
   - Example: `https://abc123@o123456.ingest.sentry.io/123456`
   - Required: **Yes**
   - How to get: From your Sentry project settings → Client Keys (DSN)

2. **ENVIRONMENT**
   - Description: Application environment identifier
   - Value: `production`
   - Required: **Yes**

3. **SENTRY_ENVIRONMENT**
   - Description: Sentry-specific environment tag
   - Value: `production`
   - Required: No (defaults to ENVIRONMENT value)

### Optional Performance & Debug Variables

4. **SENTRY_DEBUG**
   - Description: Enable Sentry debug mode
   - Value: `false` (for production)
   - Required: No (defaults to false)

5. **SENTRY_TRACES_SAMPLE_RATE**
   - Description: Performance monitoring sample rate (0.0 to 1.0)
   - Value: `0.1` (10% of transactions)
   - Required: No (defaults to 0.1)

6. **SENTRY_PROFILES_SAMPLE_RATE**
   - Description: Profiling sample rate (0.0 to 1.0)
   - Value: `0.1` (10% of transactions)
   - Required: No (defaults to 0.1)

## How to Configure in Railway

1. Go to your Railway project dashboard
2. Select your service (monkey-coder)
3. Navigate to the "Variables" tab
4. Add each variable using the "New Variable" button
5. Save and redeploy

## Verification

After deployment, you can verify Sentry is working by:

1. Checking Railway logs for: "Sentry configured for core in production environment"
2. Visiting your Sentry dashboard to see if the project appears
3. Testing with `/health` endpoint - should not trigger Sentry
4. Any application errors should now appear in your Sentry dashboard

## Troubleshooting

If Sentry isn't working:

1. **Check logs for warnings**: Look for "SENTRY_DSN not configured, Sentry disabled"
2. **Verify DSN format**: Must start with `https://` and contain valid project ID
3. **Check Sentry project status**: Ensure your Sentry project is active
4. **Test locally**: Set the same environment variables locally and test

## Example Configuration

```bash
# In Railway Variables tab, add:
SENTRY_DSN=https://your-key@o123456.ingest.sentry.io/your-project-id
ENVIRONMENT=production
SENTRY_ENVIRONMENT=production
SENTRY_DEBUG=false
SENTRY_TRACES_SAMPLE_RATE=0.1
```

## Security Note

- Never commit your SENTRY_DSN to version control
- Use Railway's environment variables for secure storage
- The DSN is safe to use in client-side code but keep it in environment variables for flexibility
