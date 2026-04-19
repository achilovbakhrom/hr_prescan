<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Message from 'primevue/message'
import AuthShell from '../components/AuthShell.vue'
import { authService } from '../services/auth.service'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const route = useRoute()
const { t } = useI18n()

const loading = ref(true)
const success = ref(false)
const errorMessage = ref<string | null>(null)

onMounted(async () => {
  const token = route.query.token
  if (typeof token !== 'string' || !token) {
    errorMessage.value = 'Invalid or missing verification token.'
    loading.value = false
    return
  }

  try {
    await authService.verifyEmail(token)
    success.value = true
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error ? err.message : 'Email verification failed. The link may have expired.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <AuthShell>
    <div v-if="loading" class="flex flex-col items-center gap-4 py-6 text-center">
      <i class="pi pi-spin pi-spinner text-3xl text-[color:var(--color-accent)]"></i>
      <p class="text-sm text-[color:var(--color-text-secondary)]">
        {{ t('auth.verifyEmail.verifying') }}
      </p>
    </div>

    <div v-else-if="success" class="text-center">
      <div
        class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-[color:var(--color-accent-celebrate-soft)]"
      >
        <i class="pi pi-check text-2xl text-[color:var(--color-accent-celebrate)]"></i>
      </div>
      <h1 class="mb-3 text-xl font-semibold text-[color:var(--color-text-primary)] sm:text-2xl">
        {{ t('auth.verifyEmail.success') }}
      </h1>
      <RouterLink :to="{ name: ROUTE_NAMES.LOGIN }">
        <Button :label="t('auth.verifyEmail.goToLogin')" class="mt-2 w-full" />
      </RouterLink>
    </div>

    <div v-else class="text-center">
      <div
        class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-[color:var(--color-surface-sunken)]"
      >
        <i class="pi pi-times text-2xl text-[color:var(--color-danger)]"></i>
      </div>
      <h1 class="mb-3 text-xl font-semibold text-[color:var(--color-text-primary)] sm:text-2xl">
        {{ t('auth.verifyEmail.error') }}
      </h1>
      <Message v-if="errorMessage" severity="error" class="mb-4">
        {{ errorMessage }}
      </Message>
      <RouterLink :to="{ name: ROUTE_NAMES.LOGIN }">
        <Button :label="t('auth.verifyEmail.goToLogin')" severity="secondary" class="mt-2 w-full" />
      </RouterLink>
    </div>
  </AuthShell>
</template>
