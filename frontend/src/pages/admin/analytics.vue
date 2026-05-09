<script setup lang="ts">
import AdminAnalyticsPage from '@/features/admin/pages/AdminAnalyticsPage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.ADMIN_ANALYTICS,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.ADMIN],
})
</script>

<template>
  <AdminAnalyticsPage />
</template>
