# Supabase OAuth Integration

This directory contains the Supabase client configuration for OAuth authentication.

## Setup

1. Create a Supabase project at https://supabase.com
2. Enable OAuth providers (Google, GitHub) in Authentication > Providers
3. Configure environment variables:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

4. Configure OAuth redirect URLs in your Supabase project:
   - Development: `http://localhost:3000/auth/callback`
   - Production: `https://your-domain.com/auth/callback`

## Usage

The Supabase client is automatically initialized in the login page for OAuth flows.

### Google/GitHub Login

Click the OAuth buttons on the login page to authenticate with Google or GitHub.

## Files

- `client.ts` - Supabase client initialization with browser-side auth configuration
