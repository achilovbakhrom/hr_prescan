import { fileURLToPath, URL } from 'node:url'

import tailwindcss from '@tailwindcss/vite'

const devProxyTarget = process.env.VITE_DEV_PROXY_TARGET

export default defineNuxtConfig({
  compatibilityDate: '2026-05-09',
  srcDir: 'src',
  devtools: { enabled: false },
  css: [
    '@fontsource/geist-sans/400.css',
    '@fontsource/geist-sans/500.css',
    '@fontsource/geist-sans/600.css',
    '@fontsource/geist-sans/700.css',
    '@fontsource/geist-mono/400.css',
    '@fontsource/geist-mono/500.css',
    '@/assets/styles/main.css',
    '@/assets/styles/primevue-overrides.css',
    '@/assets/styles/dark-mode.css',
  ],
  alias: {
    '@': fileURLToPath(new URL('./src', import.meta.url)),
  },
  app: {
    head: {
      title: 'PreScreen AI - AI-Powered Candidate Screening',
      meta: [
        { name: 'title', content: 'PreScreen AI - AI-Powered Candidate Screening' },
        {
          name: 'description',
          content:
            'Screen hundreds of candidates automatically with AI video interviews. Save time, reduce bias, and hire the best talent faster.',
        },
        { name: 'author', content: 'PreScreen AI' },
        { name: 'robots', content: 'index, follow' },
        { property: 'og:type', content: 'website' },
        { property: 'og:url', content: 'https://prescreen-app.com/' },
        { property: 'og:title', content: 'PreScreen AI - AI-Powered Candidate Screening' },
        {
          property: 'og:description',
          content:
            'Screen hundreds of candidates automatically with AI video interviews. Save time, reduce bias, and hire the best talent faster.',
        },
        { property: 'og:image', content: 'https://prescreen-app.com/og-image.png' },
        { property: 'og:image:alt', content: 'PreScreen AI social preview' },
        { property: 'og:image:width', content: '1200' },
        { property: 'og:image:height', content: '630' },
        { property: 'og:site_name', content: 'PreScreen AI' },
        { property: 'og:locale', content: 'en_US' },
        { name: 'twitter:card', content: 'summary_large_image' },
        { name: 'twitter:url', content: 'https://prescreen-app.com/' },
        { name: 'twitter:title', content: 'PreScreen AI - AI-Powered Candidate Screening' },
        {
          name: 'twitter:description',
          content:
            'Screen hundreds of candidates automatically with AI video interviews. Save time, reduce bias, and hire the best talent faster.',
        },
        { name: 'twitter:image', content: 'https://prescreen-app.com/og-image.png' },
        { name: 'twitter:image:alt', content: 'PreScreen AI social preview' },
        { name: 'theme-color', content: '#2563EB' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'canonical', href: 'https://prescreen-app.com/' },
      ],
    },
  },
  vite: {
    plugins: [tailwindcss()],
    server: {
      allowedHosts: true,
      proxy: devProxyTarget
        ? {
            '/api': {
              target: devProxyTarget,
              changeOrigin: true,
              secure: false,
            },
          }
        : undefined,
    },
  },
})
