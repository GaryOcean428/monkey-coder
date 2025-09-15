import path from 'node:path'
import { PHASE_DEVELOPMENT_SERVER } from 'next/constants.js'

/**
 * @param {boolean} isDev
 * @returns {import('next').NextConfig}
 */
const createConfig = (isDev) => {
  // For Railway deployment, use standalone mode when in production
  const isRailwayProduction = process.env.RAILWAY_ENVIRONMENT === 'production'
  // Allow forcing static export via environment variable
  const forceStaticExport = process.env.NEXT_OUTPUT_EXPORT === 'true'
  
  // Set environment variable defaults to prevent build failures
  if (!process.env.NEXTAUTH_URL) {
    process.env.NEXTAUTH_URL = 'https://coder.fastmonkey.au'
  }
  if (!process.env.NEXTAUTH_SECRET) {
    process.env.NEXTAUTH_SECRET = `nextjs-build-secret-${Date.now()}`
  }
  if (!process.env.NEXT_PUBLIC_API_URL) {
    process.env.NEXT_PUBLIC_API_URL = 'https://coder.fastmonkey.au'
  }
  if (!process.env.NEXT_PUBLIC_APP_URL) {
    process.env.NEXT_PUBLIC_APP_URL = 'https://coder.fastmonkey.au'
  }
  if (!process.env.DATABASE_URL) {
    process.env.DATABASE_URL = 'postgresql://localhost:5432/placeholder'
  }
  
  return {
    reactStrictMode: true,
    // Use export mode for local/unified deployment, standalone for Railway multi-service
    // But allow forcing static export for unified deployments
    output: (isRailwayProduction && !forceStaticExport) ? undefined : 'export',
    trailingSlash: !(isRailwayProduction && !forceStaticExport), // Only use trailing slash for static export
    images: {
      unoptimized: !(isRailwayProduction && !forceStaticExport), // Only unoptimize for static export
      domains: ['localhost', 'monkey-coder.up.railway.app'],
    },

    // Proxy API routes in dev mode (non-Railway production)
    ...(isDev && !isRailwayProduction ? {
      async rewrites () {
        return [
          {
            source: '/api/:path*',
            destination: process.env.NEXT_PUBLIC_API_URL
              ? `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`
              : 'http://127.0.0.1:8000/api/:path*',
          },
        ]
      },
    } : {}),
    
    webpack: (config, { isServer, dev }) => {
      // Add path alias for both development and production builds
      config.resolve.alias = {
        ...config.resolve.alias,
        '@': path.resolve(process.cwd(), 'src'),
      }

      // Additional webpack optimizations for production builds
      if (!dev && !isServer) {
        config.resolve.fallback = {
          ...config.resolve.fallback,
          fs: false,
          module: false,
        }
      }

      return config
    },
    experimental: {
      optimizeCss: false, // Disable CSS optimization to reduce inline styles
      externalDir: true // Required for monorepo support
    }
  }
}

export default (phase) => {
  const isDev = phase === PHASE_DEVELOPMENT_SERVER
  return createConfig(isDev)
}
