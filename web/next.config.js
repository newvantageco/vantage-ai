/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  compiler: {
    removeConsole: false,
  },
  experimental: {
    // Remove all experimental features
  },
  // Minimal configuration for debugging
  output: 'standalone',
  trailingSlash: false,
  // Skip static optimization
  skipTrailingSlashRedirect: true,
  // Disable static optimization
  staticPageGenerationTimeout: 1000,
};

module.exports = nextConfig;

