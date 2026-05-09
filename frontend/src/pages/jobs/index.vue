<script setup lang="ts">
import PublicJobBoardPage from '@/features/vacancies/pages/PublicJobBoardPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.JOB_BOARD,
  layout: 'public',
  requiresAuth: false,
  seo: {
    title: 'AI Screening Jobs | PreScreen AI',
    description:
      'Browse public vacancies that use PreScreen AI for fast, structured candidate screening.',
    path: '/jobs',
  },
})
</script>

<template>
  <PublicJobBoardPage />
</template>
