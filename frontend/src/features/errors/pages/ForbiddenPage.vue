<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const { t } = useI18n()
const router = useRouter()

function goHome(): void {
  router.push({ name: ROUTE_NAMES.DASHBOARD })
}

function goBack(): void {
  router.back()
}
</script>

<template>
  <div
    class="flex min-h-screen flex-col items-center justify-center bg-gray-50 px-6 py-24"
  >
    <div class="text-center">
      <p class="text-8xl font-extrabold text-amber-500">403</p>
      <h1 class="mt-4 text-3xl font-bold tracking-tight text-gray-900">
        {{ t('errors.forbidden') }}
      </h1>
      <p class="mt-4 text-lg text-gray-600">
        {{ t('errors.forbiddenDesc') }}
      </p>
      <div class="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
        <Button
          :label="t('errors.goHome')"
          icon="pi pi-home"
          @click="goHome"
        />
        <Button
          :label="t('errors.goBack')"
          icon="pi pi-arrow-left"
          text
          severity="secondary"
          @click="goBack"
        />
      </div>
    </div>
    <div class="mt-16 text-center">
      <p class="text-sm text-gray-400">
        {{ t('errors.needAccess') }}
        <a href="mailto:support@hrprescan.com" class="text-blue-600 hover:underline"
          >support@hrprescan.com</a
        >
      </p>
    </div>
  </div>
</template>
