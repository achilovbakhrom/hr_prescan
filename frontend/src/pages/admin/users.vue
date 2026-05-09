<script setup lang="ts">
import AdminUsersPage from '@/features/admin/pages/AdminUsersPage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.ADMIN_USERS,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.ADMIN],
})
</script>

<template>
  <AdminUsersPage />
</template>
