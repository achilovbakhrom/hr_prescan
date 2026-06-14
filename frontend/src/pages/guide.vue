<script setup lang="ts">
import InstructionsPage from '@/features/instructions/pages/InstructionsPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.GUIDE,
  layout: 'public',
  requiresAuth: false,
  seo: {
    title: 'How it works | PreScreen AI',
    description:
      'A step-by-step guide to PreScreen AI — create a vacancy, set up AI pre-screening and interviews, review scored candidates, and what applicants experience.',
    path: '/guide',
  },
})
</script>

<template>
  <InstructionsPage />
</template>
