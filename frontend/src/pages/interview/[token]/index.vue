<script setup lang="ts">
import InterviewGatewayPage from '@/features/interviews/pages/InterviewGatewayPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.INTERVIEW_GATEWAY, layout: false, requiresAuth: false })
</script>

<template>
  <InterviewGatewayPage />
</template>
