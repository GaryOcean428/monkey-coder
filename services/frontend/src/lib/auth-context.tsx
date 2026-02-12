/**
 * Authentication React Context components
 * Separated from auth.ts to avoid formatting issues
 */

"use client"

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AuthUser, login, signup, logout, getUserStatus, refreshToken, exchangeSupabaseToken, clearLegacyTokens } from './auth';
import { createClient, isConfigured as isSupabaseConfigured } from './supabase/client';

interface AuthContextType {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (data: {
    username: string;
    name: string;
    email: string;
    password: string;
    plan?: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Clear any legacy tokens during migration
        clearLegacyTokens();

        // First try backend auth status (httpOnly cookies)
        const status = await getUserStatus();
        if (status.authenticated && status.user) {
          setUser(status.user);
          return;
        }

        // If backend auth failed and Supabase is configured, check for Supabase session
        if (isSupabaseConfigured) {
          const supabase = createClient();
          const { data: { session } } = await supabase.auth.getSession();
          if (session?.access_token) {
            try {
              const result = await exchangeSupabaseToken(session.access_token);
              if (result.user) {
                setUser(result.user);
              }
            } catch (bridgeErr) {
              console.warn('Supabase session exists but backend exchange failed:', bridgeErr);
            }
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Setup token refresh interval
  useEffect(() => {
    if (!user) return;

    const refreshInterval = setInterval(async () => {
      try {
        const result = await refreshToken();
        if (result && result.user) {
          setUser(result.user);
        } else {
          // Token refresh failed, logout user
          await logout();
          setUser(null);
        }
      } catch (error) {
        console.error('Token refresh failed:', error);
      }
    }, 15 * 60 * 1000); // Refresh every 15 minutes

    return () => clearInterval(refreshInterval);
  }, [user]);

  const handleLogin = async (email: string, password: string) => {
    const result = await login(email, password);
    setUser(result.user);
  };

  const handleSignup = async (data: {
    username: string;
    name: string;
    email: string;
    password: string;
    plan?: string;
  }) => {
    const result = await signup(data);
    setUser(result.user);
  };

  const handleLogout = async () => {
    await logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login: handleLogin,
        signup: handleSignup,
        logout: handleLogout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

/**
 * Higher-order component for protecting routes
 */
export function withAuth<P extends object>(
  Component: React.ComponentType<P>
): React.FC<P> {
  return function AuthenticatedComponent(props: P) {
    const { user, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!loading && !user) {
        router.push('/login');
      }
    }, [user, loading, router]);

    if (loading) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      );
    }

    if (!user) {
      return null; // Will redirect in useEffect
    }

    return <Component {...props} />;
  };
}
