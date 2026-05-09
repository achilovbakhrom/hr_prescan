<script setup lang="ts">
import ProfilePage from '@/features/settings/pages/ProfilePage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.PROFILE, layout: 'app', requiresAuth: true })
</script>

<template>
  <ProfilePage />
</template>
