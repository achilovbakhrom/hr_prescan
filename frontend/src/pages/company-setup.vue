<script setup lang="ts">
import CompanySetupPage from '@/features/auth/pages/CompanySetupPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.COMPANY_SETUP, layout: 'public', requiresAuth: false })
</script>

<template>
  <CompanySetupPage />
</template>
