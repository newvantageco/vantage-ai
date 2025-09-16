/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: false, // Disable SWC temporarily
  compiler: {
    removeConsole: false,
  },
  experimental: {
    // Remove all experimental features
  },
  // Minimal configuration for debugging
  output: 'standalone',
};

module.exports = nextConfig;

