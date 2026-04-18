<script setup lang="ts">
import { watch } from 'vue'
import { RouterView } from 'vue-router'
import { useI18n } from 'vue-i18n'
import CookieConsent from '@/shared/components/CookieConsent.vue'
import AIAssistantDrawer from '@/shared/components/AIAssistantDrawer.vue'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { authService } from '@/features/auth/services/auth.service'
import { setLocale } from '@/shared/i18n'

const { locale } = useI18n()
const authStore = useAuthStore()

// Keep the authenticated user's persisted language in sync with the UI locale
// so backend AI assistants (prescreen chat, question generation) follow the
// user's current language choice — even if they switch mid-session.
watch(locale, (next) => {
  const code = next as 'en' | 'ru' | 'uz'
  if (!authStore.isAuthenticated) return
  if (authStore.user?.language === code) return
  authService
    .updateMe({ language: code })
    .then((u) => {
      authStore.user = u
    })
    .catch(() => {
      /* non-critical; retried on next /me refresh */
    })
})

// On login (or /me refresh) pull the UI locale from the persisted user.language.
watch(
  () => authStore.user?.language,
  (next) => {
    if (next && next !== locale.value) setLocale(next)
  },
  { immediate: true },
)
</script>

<template>
  <RouterView />
  <CookieConsent />
  <AIAssistantDrawer />
</template>
