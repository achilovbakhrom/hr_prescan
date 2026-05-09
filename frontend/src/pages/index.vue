<script setup lang="ts">
import LandingPage from '@/features/landing/pages/LandingPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.LANDING,
  layout: false,
  requiresAuth: false,
  seo: {
    title: 'PreScreen AI - AI-Powered Candidate Screening',
    description:
      'Automate candidate prescreening with AI interviews, multilingual vacancy workflows, and structured hiring insights.',
    path: '/',
  },
})
</script>

<template>
  <LandingPage />
</template>
