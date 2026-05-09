<script setup lang="ts">
import TermsOfServicePage from '@/features/legal/pages/TermsOfServicePage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.TERMS_OF_SERVICE,
  layout: 'public',
  requiresAuth: false,
  seo: {
    title: 'Terms of Service | PreScreen AI',
    description: 'Review the terms that govern use of the PreScreen AI platform.',
    path: '/terms',
  },
})
</script>

<template>
  <TermsOfServicePage />
</template>
