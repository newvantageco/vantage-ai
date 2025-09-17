/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output for Docker
  output: 'standalone',
  
  // Enable experimental features for better performance
  experimental: {
    // Enable server components
    serverComponentsExternalPackages: ['@clerk/nextjs'],
    
    // Enable optimized package imports
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
  },

  // Image optimization
  images: {
    domains: ['localhost', 'images.unsplash.com'],
    formats: ['image/webp', 'image/avif'],
  },

  // Compiler optimizations
  compiler: {
    // Remove console.log in production
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // Webpack optimizations
  webpack: (config, { dev, isServer }) => {
    // Optimize bundle size
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: {
            minChunks: 2,
            priority: -20,
            reuseExistingChunk: true,
          },
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            priority: -10,
            chunks: 'all',
          },
        },
      }
    }

    return config
  },

  // Headers for security and performance
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ]
  },

  // Redirects for better UX
  async redirects() {
    return [
      {
        source: '/',
        destination: '/public-calendar',
        permanent: false,
      },
    ]
  },

  // Environment variables validation
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },

  // TypeScript configuration
  typescript: {
    // Dangerously allow production builds to successfully complete even if
    // your project has type errors.
    ignoreBuildErrors: false,
  },

  // ESLint configuration
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: false,
  },

  // Performance optimizations
  poweredByHeader: false,
  generateEtags: false,
  
  // Compression
  compress: true,
  
  // Trailing slash handling
  trailingSlash: false,
}

module.exports = nextConfig
