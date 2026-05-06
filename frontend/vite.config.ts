import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

const devProxyTarget = process.env.VITE_DEV_PROXY_TARGET

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
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
})
