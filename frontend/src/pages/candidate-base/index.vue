<script setup lang="ts">
import CandidateBasePage from '@/features/candidates/pages/CandidateBasePage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.CANDIDATE_BASE,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
})
</script>

<template>
  <CandidateBasePage />
</template>
