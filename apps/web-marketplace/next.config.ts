import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow an isolated build dir (e.g. a parallel preview instance) so two dev
  // servers don't corrupt a shared .next. Defaults to ".next".
  distDir: process.env.NEXT_DIST_DIR || ".next",
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
  transpilePackages: ["@skillsgit/ui", "@skillsgit/api-client"],
};

export default nextConfig;
