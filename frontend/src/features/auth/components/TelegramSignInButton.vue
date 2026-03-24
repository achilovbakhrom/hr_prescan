<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { apiClient } from '@/shared/api/client'
import type { LoginResponse } from '../types/auth.types'

interface TelegramAuthResponse {
  code: string
  linkUrl: string
  expiresAt: string
}

interface TelegramAuthCheckResponse {
  status: 'pending' | 'authenticated'
  tokens?: LoginResponse['tokens']
  user?: LoginResponse['user']
}

const emit = defineEmits<{
  success: [data: LoginResponse]
  error: [message: string]
}>()

const { t } = useI18n()
const loading = ref(false)
const polling = ref(false)
let pollTimer: ReturnType<typeof setInterval> | null = null

async function handleClick(): Promise<void> {
  loading.value = true

  // Open window synchronously (in click context) to avoid popup blocker
  const popup = window.open('', '_blank')

  try {
    const { data } = await apiClient.post<TelegramAuthResponse>('/telegram/auth/request/')

    // Navigate the already-opened window to the Telegram link
    if (popup) {
      popup.location.href = data.linkUrl
    } else {
      // Fallback if popup was still blocked
      window.location.href = data.linkUrl
    }

    polling.value = true
    loading.value = false
    startPolling(data.code)
  } catch {
    popup?.close()
    loading.value = false
    emit('error', t('auth.telegram.requestFailed'))
  }
}

function startPolling(code: string): void {
  let attempts = 0
  const maxAttempts = 60 // 5 minutes at 5s intervals

  pollTimer = setInterval(async () => {
    attempts++
    if (attempts > maxAttempts) {
      stopPolling()
      emit('error', t('auth.telegram.expired'))
      return
    }

    try {
      const { data } = await apiClient.get<TelegramAuthCheckResponse>(
        `/telegram/auth/check/${code}/`,
      )

      if (data.status === 'authenticated' && data.tokens && data.user) {
        stopPolling()
        emit('success', { tokens: data.tokens, user: data.user })
      }
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status
      if (status === 410 || status === 404) {
        // Expired or invalid
        stopPolling()
        emit('error', t('auth.telegram.expired'))
      }
    }
  }, 5000)
}

function stopPolling(): void {
  polling.value = false
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}
</script>

<template>
  <div class="mb-4">
    <Button
      :label="polling ? t('auth.telegram.waiting') : t('auth.telegram.signIn')"
      :loading="loading"
      :disabled="polling"
      icon="pi pi-telegram"
      class="w-full"
      severity="info"
      outlined
      @click="handleClick"
    />
    <p v-if="polling" class="mt-2 text-center text-xs text-gray-500">
      {{ t('auth.telegram.openApp') }}
    </p>
  </div>
</template>
