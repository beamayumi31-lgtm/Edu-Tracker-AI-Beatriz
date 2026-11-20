import type { NextConfig } from 'next';

// A distribuição Node permite publicar o mesmo frontend na VPS, mantendo o fluxo local Vinext.
const nextConfig: NextConfig = {
  // Vinext gera seus tipos em .next; separar evita sobrescrita ao alternar os dois modos.
  distDir: '.next-hostinger',
  output: 'standalone',
  poweredByHeader: false,
};

export default nextConfig;
