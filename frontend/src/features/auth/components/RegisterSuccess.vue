<script setup lang="ts">
import { ROUTE_NAMES } from '@/shared/constants/routes'

defineProps<{
  email: string
}>()
</script>

<template>
  <div class="text-center">
    <h1 class="mb-4 text-2xl font-bold text-gray-900">Check Your Email</h1>
    <p class="mb-6 text-gray-600">
      We've sent a verification link to <strong>{{ email }}</strong
      >. Please check your inbox and click the link to activate your account.
    </p>
    <RouterLink
      :to="{ name: ROUTE_NAMES.LOGIN }"
      class="font-medium text-blue-600 dark:text-blue-400 hover:text-blue-500"
      >Back to Login</RouterLink
    >
  </div>
</template>
