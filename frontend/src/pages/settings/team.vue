<script setup lang="ts">
import TeamManagementPage from '@/features/settings/pages/TeamManagementPage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.TEAM_MANAGEMENT,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.ADMIN],
})
</script>

<template>
  <TeamManagementPage />
</template>
