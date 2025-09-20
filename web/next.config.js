/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  compiler: {
    removeConsole: false,
  },
  experimental: {
    serverActions: { bodySizeLimit: '2mb' }
  },
  // Production optimizations
  output: 'standalone',
  trailingSlash: false,
  // Skip static optimization
  skipTrailingSlashRedirect: true,
  // Disable automatic redirects
  redirects: async () => [],
  // Disable static optimization
  staticPageGenerationTimeout: 1000,
};

module.exports = nextConfig;

