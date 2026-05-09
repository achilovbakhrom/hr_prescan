<script setup lang="ts">
import ServerErrorPage from '@/features/errors/pages/ServerErrorPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.SERVER_ERROR, layout: false, requiresAuth: false })
</script>

<template>
  <ServerErrorPage />
</template>
