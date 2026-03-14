<script setup lang="ts">
import { useAuthStore } from '@/features/auth/stores/auth.store'

const authStore = useAuthStore()
</script>

<template>
  <div class="p-6">
    <h1 class="text-3xl font-bold text-gray-900">
      Welcome, {{ authStore.user?.firstName ?? 'User' }}!
    </h1>
    <p class="mt-2 text-gray-600">
      This is your dashboard. More features are coming soon.
    </p>
  </div>
</template>
