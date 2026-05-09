<script setup lang="ts">
import ForbiddenPage from '@/features/errors/pages/ForbiddenPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.FORBIDDEN, layout: false, requiresAuth: false })
</script>

<template>
  <ForbiddenPage />
</template>
