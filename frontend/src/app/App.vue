<script setup lang="ts">
import { RouterView } from 'vue-router'
import CookieConsent from '@/shared/components/CookieConsent.vue'
import AIAssistantDrawer from '@/shared/components/AIAssistantDrawer.vue'
import { useThemeStore } from '@/shared/stores/theme.store'

// Initialise theme store early so the `.dark` class is applied before any
// route renders (watcher with `immediate: true` handles first paint).
useThemeStore()

// AnimatedBackground + FloatingBackgroundPicker are mounted by `PageShell`,
// which wraps `AppLayout` and `PublicLayout`. Page-level routes that sit
// outside those layouts (e.g. the landing page, public interview, error
// routes) will adopt PageShell in Wave 8.

// Locale ↔ user.language sync is owned by `useLocale.switchLocale` (write path)
// and `auth.store.syncPreferredLanguage` (read path, called from setAuth /
// fetchUser). Keeping them single-sourced avoids duplicate PATCH /auth/me/
// calls that were tripping nginx's auth rate limit.
</script>

<template>
  <RouterView />
  <CookieConsent />
  <AIAssistantDrawer />
</template>
