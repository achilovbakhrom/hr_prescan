<script setup lang="ts">
import VerifyEmailPage from '@/features/auth/pages/VerifyEmailPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.VERIFY_EMAIL, layout: 'auth', requiresAuth: false })
</script>

<template>
  <VerifyEmailPage />
</template>
