<script setup lang="ts">
import { ROUTE_NAMES } from '@/shared/constants/routes'

defineProps<{
  email: string
}>()
</script>

<template>
  <div class="text-center">
    <div
      class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-[color:var(--color-accent-soft)]"
    >
      <i class="pi pi-envelope text-2xl text-[color:var(--color-accent)]"></i>
    </div>
    <h1 class="mb-3 text-xl font-semibold text-[color:var(--color-text-primary)] sm:text-2xl">
      Check Your Email
    </h1>
    <p class="mb-6 text-sm text-[color:var(--color-text-secondary)]">
      We've sent a verification link to <strong>{{ email }}</strong
      >. Please check your inbox and click the link to activate your account.
    </p>
    <RouterLink
      :to="{ name: ROUTE_NAMES.LOGIN }"
      class="text-sm font-medium text-[color:var(--color-accent)] hover:underline"
    >
      Back to Login
    </RouterLink>
  </div>
</template>
