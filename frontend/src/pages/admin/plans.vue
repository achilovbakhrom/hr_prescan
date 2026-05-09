<script setup lang="ts">
import AdminPlansPage from '@/features/admin/pages/AdminPlansPage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.ADMIN_PLANS,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.ADMIN],
})
</script>

<template>
  <AdminPlansPage />
</template>
