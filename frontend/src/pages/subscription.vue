<script setup lang="ts">
import SubscriptionPage from '@/features/subscriptions/pages/SubscriptionPage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.SUBSCRIPTION,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.ADMIN],
})
</script>

<template>
  <SubscriptionPage />
</template>
