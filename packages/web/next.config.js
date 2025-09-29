/** @type {import('next').NextConfig} */
const nextConfig = {
  output: process.env.NEXT_OUTPUT_EXPORT === 'true' ? 'export' : undefined,
  images: {
    unoptimized: true
  },
  trailingSlash: true
};

export default nextConfig;
