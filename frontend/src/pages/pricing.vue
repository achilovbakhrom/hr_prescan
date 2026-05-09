<script setup lang="ts">
import PricingPage from '@/features/subscriptions/pages/PricingPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.PRICING,
  layout: 'public',
  requiresAuth: false,
  seo: {
    title: 'Pricing | PreScreen AI',
    description:
      'Choose a PreScreen AI plan for AI-powered candidate screening and hiring automation.',
    path: '/pricing',
  },
})
</script>

<template>
  <PricingPage />
</template>
