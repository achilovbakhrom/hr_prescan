<script setup lang="ts">
import MyApplicationsPage from '@/features/candidates/pages/MyApplicationsPage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.MY_APPLICATIONS,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.CANDIDATE],
})
</script>

<template>
  <MyApplicationsPage />
</template>
