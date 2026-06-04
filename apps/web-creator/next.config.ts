import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      // Placeholder — production R2 / S3 bucket domains go here.
      { protocol: "https", hostname: "images.unsplash.com" },
      { protocol: "https", hostname: "avatars.githubusercontent.com" },
    ],
  },
  experimental: {
    typedRoutes: true,
  },
  transpilePackages: [
    "@skillsgit/ui",
    "@skillsgit/api-client",
    "@skillsgit/skills-schema",
  ],
};

export default nextConfig;
