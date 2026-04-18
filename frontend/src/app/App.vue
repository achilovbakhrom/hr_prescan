<script setup lang="ts">
import { RouterView } from 'vue-router'
import CookieConsent from '@/shared/components/CookieConsent.vue'
import AIAssistantDrawer from '@/shared/components/AIAssistantDrawer.vue'

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
