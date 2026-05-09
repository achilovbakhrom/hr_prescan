<script setup lang="ts">
import RegisterPage from '@/features/auth/pages/RegisterPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.REGISTER, layout: 'public', requiresAuth: false })
</script>

<template>
  <RegisterPage />
</template>
