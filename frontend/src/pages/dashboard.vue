<script setup lang="ts">
import DashboardPage from '@/features/dashboard/pages/DashboardPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.DASHBOARD, layout: 'app', requiresAuth: true })
</script>

<template>
  <DashboardPage />
</template>
