<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import ErrorShell from '../components/ErrorShell.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const { t } = useI18n()
const router = useRouter()

function goHome(): void {
  router.push({ name: ROUTE_NAMES.DASHBOARD })
}

function reload(): void {
  window.location.reload()
}
</script>

<template>
  <!-- 500 — Mesh (in-motion) per spec §9. -->
  <ErrorShell background="mesh" code="500">
    <template #title>
      <h1
        class="mt-4 text-2xl font-semibold tracking-tight text-[color:var(--color-text-primary)] sm:text-3xl"
      >
        {{ t('errors.serverError') }}
      </h1>
    </template>
    <template #description>
      <p class="mt-3 text-base text-[color:var(--color-text-secondary)]">
        {{ t('errors.serverErrorDesc') }}
      </p>
    </template>
    <template #actions>
      <Button :label="t('errors.tryAgain')" icon="pi pi-refresh" @click="reload" />
      <Button
        :label="t('errors.goHome')"
        icon="pi pi-home"
        text
        severity="secondary"
        @click="goHome"
      />
    </template>
    <template #footer>
      {{ t('errors.urgentSupport') }}
      <a
        href="mailto:support@hrprescan.com"
        class="text-[color:var(--color-accent)] hover:underline"
        >support@hrprescan.com</a
      >
    </template>
  </ErrorShell>
</template>
