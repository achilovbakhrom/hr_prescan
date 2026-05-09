<script setup lang="ts">
import PrivacyPolicyPage from '@/features/legal/pages/PrivacyPolicyPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.PRIVACY_POLICY,
  layout: 'public',
  requiresAuth: false,
  seo: {
    title: 'Privacy Policy | PreScreen AI',
    description: 'Read how PreScreen AI handles privacy, data processing, and user data.',
    path: '/privacy',
  },
})
</script>

<template>
  <PrivacyPolicyPage />
</template>
