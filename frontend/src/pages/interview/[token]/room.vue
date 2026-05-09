<script setup lang="ts">
import InterviewRoomPage from '@/features/interviews/pages/InterviewRoomPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.INTERVIEW_ROOM, layout: false, requiresAuth: false })
</script>

<template>
  <InterviewRoomPage />
</template>
