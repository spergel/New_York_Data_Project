/** @type {import('next').NextConfig} */
const nextConfig = {
  // Compress responses
  compress: true,
  
  // Enable static optimization
  trailingSlash: false,
  
  // Headers for better caching
  async headers() {
    return [
      {
        source: '/api/events',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=300, s-maxage=300', // 5 minutes cache
          },
        ],
      },
      {
        source: '/public/scraped_events.json',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=3600, s-maxage=3600', // 1 hour cache
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;