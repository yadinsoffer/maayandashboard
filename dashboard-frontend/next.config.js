/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  async headers() {
    return [
      {
        // Apply these headers to all routes
        source: '/(.*)',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'X-Requested-With, Content-Type, Authorization',
          },
          // Allow mixed content (HTTP requests from HTTPS)
          {
            key: 'Content-Security-Policy',
            value: "upgrade-insecure-requests; default-src 'self'; connect-src 'self' http://ec2-100-27-189-61.compute-1.amazonaws.com:5001 https://ec2-100-27-189-61.compute-1.amazonaws.com:5001; img-src 'self' data:; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self';"
          }
        ],
      },
    ];
  },
  // Allow images from EC2 domain
  images: {
    domains: ['ec2-100-27-189-61.compute-1.amazonaws.com'],
  },
  // Enable experimental features
  experimental: {
    // Remove serverActions as it's causing a warning
  },
  // Add webpack configuration for path aliases
  webpack: (config) => {
    config.resolve.alias['@'] = path.join(__dirname, 'src');
    return config;
  },
};

module.exports = nextConfig; 
