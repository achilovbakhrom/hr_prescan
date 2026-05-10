import { fileURLToPath, URL } from 'node:url'

import tailwindcss from '@tailwindcss/vite'

const devProxyTarget = process.env.VITE_DEV_PROXY_TARGET
const appTitle = 'PreScreen AI - Strict AI Candidate Prescreening'
const appDescription =
  'Add strict dynamic candidate filters, automate prescreening interviews, and let candidates complete screening by link without authentication.'

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
      title: appTitle,
      meta: [
        { name: 'title', content: appTitle },
        {
          name: 'description',
          content: appDescription,
        },
        { name: 'author', content: 'PreScreen AI' },
        { name: 'robots', content: 'index, follow' },
        { property: 'og:type', content: 'website' },
        { property: 'og:url', content: 'https://prescreen-app.com/' },
        { property: 'og:title', content: appTitle },
        {
          property: 'og:description',
          content: appDescription,
        },
        { property: 'og:image', content: 'https://prescreen-app.com/og-image.png' },
        { property: 'og:image:alt', content: 'PreScreen AI social preview' },
        { property: 'og:image:width', content: '1200' },
        { property: 'og:image:height', content: '630' },
        { property: 'og:site_name', content: 'PreScreen AI' },
        { property: 'og:locale', content: 'en_US' },
        { name: 'twitter:card', content: 'summary_large_image' },
        { name: 'twitter:url', content: 'https://prescreen-app.com/' },
        { name: 'twitter:title', content: appTitle },
        {
          name: 'twitter:description',
          content: appDescription,
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
