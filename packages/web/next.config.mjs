import path from 'node:path'

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
    domains: ['localhost', 'monkey-coder.up.railway.app'],
  },
  // Note: headers don't work with output: 'export' mode
  // We'll handle CSP and other security through meta tags in the document
  webpack: (config, { isServer, dev }) => {
    // Add path alias for both development and production builds
    // This ensures @/ resolves correctly in Docker and local environments
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

export default nextConfig
