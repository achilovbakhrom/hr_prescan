<script setup lang="ts">
import InterviewConfirmationPage from '@/features/interviews/pages/InterviewConfirmationPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.INTERVIEW_CONFIRMATION, layout: 'public', requiresAuth: false })
</script>

<template>
  <InterviewConfirmationPage />
</template>
