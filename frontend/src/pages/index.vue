<script setup lang="ts">
import LandingPage from '@/features/landing/pages/LandingPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.LANDING,
  layout: false,
  requiresAuth: false,
  seo: {
    title: 'PreScreen AI - Strict AI Candidate Prescreening',
    description:
      'Add strict dynamic candidate filters, automate prescreening interviews, and let candidates complete screening by link without authentication.',
    path: '/',
  },
})
</script>

<template>
  <LandingPage />
</template>
