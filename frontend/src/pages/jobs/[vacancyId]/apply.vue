<script setup lang="ts">
import ApplicationFormPage from '@/features/candidates/pages/ApplicationFormPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.JOB_APPLY,
  layout: 'public',
  requiresAuth: false,
})
</script>

<template>
  <ApplicationFormPage />
</template>
