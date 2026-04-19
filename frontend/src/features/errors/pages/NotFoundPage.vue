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

function goBack(): void {
  router.back()
}
</script>

<template>
  <!-- 404 — Aurora (playful) per spec §9. -->
  <ErrorShell background="aurora" code="404">
    <template #title>
      <h1
        class="mt-4 text-2xl font-semibold tracking-tight text-[color:var(--color-text-primary)] sm:text-3xl"
      >
        {{ t('errors.notFound') }}
      </h1>
    </template>
    <template #description>
      <p class="mt-3 text-base text-[color:var(--color-text-secondary)]">
        {{ t('errors.notFoundDesc') }}
      </p>
    </template>
    <template #actions>
      <Button :label="t('errors.goHome')" icon="pi pi-home" @click="goHome" />
      <Button
        :label="t('errors.goBack')"
        icon="pi pi-arrow-left"
        text
        severity="secondary"
        @click="goBack"
      />
    </template>
    <template #footer>
      If you believe this is an error, please contact
      <a
        href="mailto:support@hrprescan.com"
        class="text-[color:var(--color-accent)] hover:underline"
        >support@hrprescan.com</a
      >
    </template>
  </ErrorShell>
</template>
