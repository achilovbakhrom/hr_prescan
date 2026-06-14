<script setup lang="ts">
import InstructionsPage from '@/features/instructions/pages/InstructionsPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.INSTRUCTIONS,
  layout: 'app',
  requiresAuth: true,
  roles: ['admin', 'hr'],
})
</script>

<template>
  <InstructionsPage />
</template>
