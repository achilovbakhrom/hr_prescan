<script setup lang="ts">
import PublicCvPage from '@/features/cv-builder/pages/PublicCvPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.PUBLIC_CV, layout: 'public', requiresAuth: false })
</script>

<template>
  <PublicCvPage />
</template>
