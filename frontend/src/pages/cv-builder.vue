<script setup lang="ts">
import CvBuilderPage from '@/features/cv-builder/pages/CvBuilderPage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.CV_BUILDER,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.CANDIDATE],
})
</script>

<template>
  <CvBuilderPage />
</template>
