<script setup lang="ts">
import MyCvsPage from '@/features/cv-builder/pages/MyCvsPage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.MY_CVS,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.CANDIDATE],
})
</script>

<template>
  <MyCvsPage />
</template>
