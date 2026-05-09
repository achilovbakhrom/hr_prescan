<script setup lang="ts">
import CompanyListPage from '@/features/companies/pages/CompanyListPage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.COMPANY_LIST,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
})
</script>

<template>
  <CompanyListPage />
</template>
