<script setup lang="ts">
import CandidateBaseDetailPage from '@/features/candidates/pages/CandidateBaseDetailPage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.CANDIDATE_BASE_DETAIL,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
})
</script>

<template>
  <CandidateBaseDetailPage />
</template>
