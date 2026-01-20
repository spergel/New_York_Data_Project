import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  compress: true, // Enable gzip compression for responses
  
  experimental: {
    optimizePackageImports: ['page-flip'], // Optimize page-flip library imports
  },
  
  // Enable React strict mode for better development
  reactStrictMode: true,
};

export default nextConfig;
