<script setup lang="ts">
import ChooseRolePage from '@/features/auth/pages/ChooseRolePage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.CHOOSE_ROLE, layout: 'auth', requiresAuth: false })
</script>

<template>
  <ChooseRolePage />
</template>
