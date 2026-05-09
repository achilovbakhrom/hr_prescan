<script setup lang="ts">
import AdminCompaniesPage from '@/features/admin/pages/AdminCompaniesPage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.ADMIN_COMPANIES,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.ADMIN],
})
</script>

<template>
  <AdminCompaniesPage />
</template>
