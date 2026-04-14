<script setup lang="ts">
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()

function goToDashboard(): void {
  router.push({ name: ROUTE_NAMES.DASHBOARD })
}
</script>

<template>
  <div class="rounded-lg border border-green-200 bg-green-50 p-8 text-center">
    <i class="pi pi-check-circle mb-4 text-5xl text-green-500"></i>
    <h1 class="mb-2 text-2xl font-bold text-gray-900">Interview Complete</h1>
    <p class="mb-2 text-gray-600">
      Thank you for completing your interview. Your responses have been recorded.
    </p>
    <p class="mb-6 text-sm text-gray-500">
      You will receive your results via email. Our team will review your interview and get back to
      you soon.
    </p>
    <Button
      label="Back to Dashboard"
      icon="pi pi-home"
      severity="secondary"
      @click="goToDashboard"
    />
  </div>
</template>
