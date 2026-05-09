<script setup lang="ts">
import LoginPage from '@/features/auth/pages/LoginPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.LOGIN, layout: 'public', requiresAuth: false })
</script>

<template>
  <LoginPage />
</template>
