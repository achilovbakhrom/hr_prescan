<script setup lang="ts">
import ChatInterviewPage from '@/features/interviews/pages/ChatInterviewPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.CHAT_INTERVIEW, layout: false, requiresAuth: false })
</script>

<template>
  <ChatInterviewPage />
</template>
