<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const { t } = useI18n()
const router = useRouter()

function goToDashboard(): void {
  router.push({ name: ROUTE_NAMES.DASHBOARD })
}
</script>

<template>
  <div class="rounded-lg border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950 p-8 text-center">
    <i class="pi pi-check-circle mb-4 text-5xl text-green-500"></i>
    <h1 class="mb-2 text-2xl font-bold text-gray-900">{{ t('interviews.postInterview.title') }}</h1>
    <p class="mb-2 text-gray-600">
      {{ t('interviews.postInterview.thankYou') }}
    </p>
    <p class="mb-6 text-sm text-gray-500">
      {{ t('interviews.postInterview.resultsByEmail') }}
    </p>
    <Button
      :label="t('interviews.postInterview.backToDashboard')"
      icon="pi pi-home"
      severity="secondary"
      @click="goToDashboard"
    />
  </div>
</template>
