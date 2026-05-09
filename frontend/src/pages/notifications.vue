<script setup lang="ts">
import NotificationsPage from '@/features/notifications/pages/NotificationsPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.NOTIFICATIONS, layout: 'app', requiresAuth: true })
</script>

<template>
  <NotificationsPage />
</template>
