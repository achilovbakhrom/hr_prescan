<script setup lang="ts">
import { RouterView } from 'vue-router'
import CookieConsent from '@/shared/components/CookieConsent.vue'
import AIAssistantDrawer from '@/shared/components/AIAssistantDrawer.vue'
</script>

<template>
  <RouterView />
  <CookieConsent />
  <AIAssistantDrawer />
</template>
