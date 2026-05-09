<script setup lang="ts">
import MyApplicationDetailPage from '@/features/candidates/pages/MyApplicationDetailPage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.MY_APPLICATION_DETAIL,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.CANDIDATE],
})
</script>

<template>
  <MyApplicationDetailPage />
</template>
