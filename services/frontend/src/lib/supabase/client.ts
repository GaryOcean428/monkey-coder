/**
 * Supabase client for browser-side authentication and OAuth
 * This provides Google and GitHub OAuth integration
 */

import { createClient as createSupabaseClient } from '@supabase/supabase-js'

// Supabase configuration from environment variables
// Supports both new publishable key (sb_publishable_xxx) and legacy anon key
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co'
const supabaseKey =
  process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ||
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
  'placeholder-key'

// Check if properly configured
export const isConfigured = !!(
  process.env.NEXT_PUBLIC_SUPABASE_URL &&
  (process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)
)

if (typeof window !== 'undefined' && !isConfigured) {
  console.warn(
    'Supabase URL or API key not configured. OAuth login will not work. ' +
    'Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY (or legacy NEXT_PUBLIC_SUPABASE_ANON_KEY).'
  )
}

/**
 * Creates a Supabase client for browser-side operations
 * Used primarily for OAuth authentication (Google, GitHub)
 */
export function createClient() {
  return createSupabaseClient(supabaseUrl, supabaseKey, {
    auth: {
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: true,
    },
  })
}
