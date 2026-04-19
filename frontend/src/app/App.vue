<script setup lang="ts">
import { RouterView } from 'vue-router'
import CookieConsent from '@/shared/components/CookieConsent.vue'
import AIAssistantDrawer from '@/shared/components/AIAssistantDrawer.vue'
import AnimatedBackground from '@/shared/components/AnimatedBackground.vue'
import { useThemeStore } from '@/shared/stores/theme.store'

// Initialise theme store early so the `.dark` class is applied before any
// route renders (watcher with `immediate: true` handles first paint).
useThemeStore()

// Locale ↔ user.language sync is owned by `useLocale.switchLocale` (write path)
// and `auth.store.syncPreferredLanguage` (read path, called from setAuth /
// fetchUser). Keeping them single-sourced avoids duplicate PATCH /auth/me/
// calls that were tripping nginx's auth rate limit.
</script>

<template>
  <AnimatedBackground />
  <div class="relative z-10">
    <RouterView v-slot="{ Component, route }">
      <Transition name="page" mode="out-in">
        <component :is="Component" :key="route.fullPath" />
      </Transition>
    </RouterView>
  </div>
  <CookieConsent />
  <AIAssistantDrawer />
</template>

<style>
.page-enter-active,
.page-leave-active {
  transition:
    opacity 0.35s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
