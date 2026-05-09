<script setup lang="ts">
import HRAnalyticsPage from '@/features/dashboard/pages/HRAnalyticsPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.HR_ANALYTICS,
  layout: 'app',
  requiresAuth: true,
  roles: ['admin', 'hr'],
})
</script>

<template>
  <HRAnalyticsPage />
</template>
