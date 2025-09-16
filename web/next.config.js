/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: { forceSwcTransforms: true },
  // PWA configuration
  async headers() {
    return [
      {
        source: '/manifest.json',
        headers: [
          {
            key: 'Content-Type',
            value: 'application/manifest+json',
          },
        ],
      },
    ];
  },
  // Enable service worker
  async rewrites() {
    return [
      {
        source: '/sw.js',
        destination: '/_next/static/sw.js',
      },
    ];
  },
};

module.exports = nextConfig;

