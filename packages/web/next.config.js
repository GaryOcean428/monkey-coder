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
  webpack: (config, { isServer }) => {
    // Add path alias for Docker builds to ensure @/ resolves correctly
    config.resolve.alias['@'] = path.join(__dirname, 'src')
    return config
  },
  experimental: {
    externalDir: true // Required for monorepo support
  }
}

module.exports = nextConfig
