/** @type {import('next').NextConfig} */
const nextConfig = {
  images: { unoptimized: true },
  env: {
    OPENROUTER_API_KEY: process.env.OPENROUTER_API_KEY,
  },
}

module.exports = nextConfig
