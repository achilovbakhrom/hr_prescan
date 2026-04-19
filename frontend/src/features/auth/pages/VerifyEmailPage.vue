<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Message from 'primevue/message'
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
  <div class="flex flex-1 items-center justify-center py-12">
    <div class="w-full max-w-md rounded-lg bg-white dark:bg-gray-800 p-8 text-center shadow-md">
      <div v-if="loading" class="flex flex-col items-center gap-4">
        <i class="pi pi-spin pi-spinner text-4xl text-blue-600"></i>
        <p class="text-gray-600">{{ t('auth.verifyEmail.verifying') }}</p>
      </div>

      <template v-else-if="success">
        <h1 class="mb-4 text-2xl font-bold text-green-700">
          {{ t('auth.verifyEmail.success') }}
        </h1>
        <p class="mb-6 text-gray-600">
          {{ t('auth.verifyEmail.success') }}
        </p>
        <RouterLink :to="{ name: ROUTE_NAMES.LOGIN }">
          <Button :label="t('auth.verifyEmail.goToLogin')" class="w-full" />
        </RouterLink>
      </template>

      <template v-else>
        <h1 class="mb-4 text-2xl font-bold text-red-700">
          {{ t('auth.verifyEmail.error') }}
        </h1>
        <Message v-if="errorMessage" severity="error" class="mb-4">
          {{ errorMessage }}
        </Message>
        <RouterLink :to="{ name: ROUTE_NAMES.LOGIN }">
          <Button :label="t('auth.verifyEmail.goToLogin')" severity="secondary" class="w-full" />
        </RouterLink>
      </template>
    </div>
  </div>
</template>
