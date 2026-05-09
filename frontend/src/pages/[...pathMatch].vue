<script setup lang="ts">
import NotFoundPage from '@/features/errors/pages/NotFoundPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.NOT_FOUND, layout: false, requiresAuth: false })
</script>

<template>
  <NotFoundPage />
</template>
