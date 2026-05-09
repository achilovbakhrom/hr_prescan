<script setup lang="ts">
import AdminDashboardPage from '@/features/admin/pages/AdminDashboardPage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.ADMIN_DASHBOARD,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.ADMIN],
})
</script>

<template>
  <AdminDashboardPage />
</template>
