<script setup lang="ts">
import { RouterView } from 'vue-router'
import CookieConsent from '@/shared/components/CookieConsent.vue'
</script>

<template>
  <RouterView />
  <CookieConsent />
</template>
