const path = require('path')

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  distDir: 'out',
  trailingSlash: true,
  images: {
    unoptimized: true,
    domains: ['localhost', 'monkey-coder.up.railway.app'],
  },
  webpack: (config, { isServer, dev }) => {
    // Add path alias for both development and production builds
    // This ensures @/ resolves correctly in Docker and local environments
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, 'src'),
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
    externalDir: true // Required for monorepo support
  }
}

module.exports = nextConfig
