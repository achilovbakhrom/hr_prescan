<template>
  <div>
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
    <ClientOnly>
      <CookieConsent />
      <AIAssistantDialog />
      <AppPreloader />
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
import CookieConsent from '@/shared/components/CookieConsent.vue'
import AIAssistantDialog from '@/shared/components/AIAssistantDialog.vue'
import AppPreloader from '@/shared/components/AppPreloader.vue'
</script>

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
