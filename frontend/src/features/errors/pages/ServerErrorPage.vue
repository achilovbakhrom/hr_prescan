<script setup lang="ts">
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()

function goHome(): void {
  router.push({ name: ROUTE_NAMES.DASHBOARD })
}

function reload(): void {
  window.location.reload()
}
</script>

<template>
  <div
    class="flex min-h-screen flex-col items-center justify-center bg-gray-50 px-6 py-24"
  >
    <div class="text-center">
      <p class="text-8xl font-extrabold text-red-500">500</p>
      <h1 class="mt-4 text-3xl font-bold tracking-tight text-gray-900">
        Internal server error
      </h1>
      <p class="mt-4 text-lg text-gray-600">
        Something went wrong on our end. Our team has been notified and is
        working to fix the issue.
      </p>
      <div class="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
        <Button
          label="Try Again"
          icon="pi pi-refresh"
          @click="reload"
        />
        <Button
          label="Go to Dashboard"
          icon="pi pi-home"
          text
          severity="secondary"
          @click="goHome"
        />
      </div>
    </div>
    <div class="mt-16 text-center">
      <p class="text-sm text-gray-400">
        Need urgent help? Contact
        <a href="mailto:support@hrprescan.com" class="text-blue-600 hover:underline"
          >support@hrprescan.com</a
        >
      </p>
    </div>
  </div>
</template>
