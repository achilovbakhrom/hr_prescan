<script setup lang="ts">
import CandidateInterviewPage from '@/features/interviews/pages/CandidateInterviewPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.CANDIDATE_INTERVIEW, layout: 'public', requiresAuth: false })
</script>

<template>
  <CandidateInterviewPage />
</template>
