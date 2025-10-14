/** @type {import('next').NextConfig} */
const nextConfig = {
  // Disable experimental features that might add modern UI elements
  experimental: {
    // Disable app directory features that might conflict with our design
  },

  // Ensure we don't add any modern CSS features
  cssModules: true,

  // Disable image optimization since we're text-only
  images: {
    unoptimized: true,
  },

  // Headers to ensure proper content types
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
