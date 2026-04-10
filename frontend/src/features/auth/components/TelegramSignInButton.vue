<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { authService } from '../services/auth.service'
import type { LoginResponse } from '../types/auth.types'

interface TelegramWidgetUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
  auth_date: number
  hash: string
}

const emit = defineEmits<{
  success: [data: LoginResponse]
  error: [message: string]
}>()

const { t } = useI18n()
const botUsername = import.meta.env.VITE_TELEGRAM_BOT_USERNAME as string
const loading = ref(false)

const callbackName = `__onTelegramAuth_${Date.now()}`

async function onTelegramAuth(user: TelegramWidgetUser): Promise<void> {
  loading.value = true
  try {
    const response = await authService.telegramAuth({
      id: user.id,
      first_name: user.first_name,
      last_name: user.last_name ?? '',
      username: user.username ?? '',
      photo_url: user.photo_url ?? '',
      auth_date: user.auth_date,
      hash: user.hash,
    })
    emit('success', response)
  } catch {
    emit('error', t('auth.telegram.requestFailed'))
  } finally {
    loading.value = false
  }
}

function openTelegramAuth(): void {
  if (loading.value || !botUsername) return
  const botId = import.meta.env.VITE_TELEGRAM_BOT_ID as string | undefined
  const origin = encodeURIComponent(window.location.origin)
  const width = 550
  const height = 470
  const left = (screen.width - width) / 2
  const top = (screen.height - height) / 2
  window.open(
    `https://oauth.telegram.org/auth?bot_id=${botId || botUsername}&origin=${origin}&request_access=write`,
    'telegram_auth',
    `width=${width},height=${height},left=${left},top=${top}`,
  )
}

function handleMessage(e: MessageEvent): void {
  if (e.origin !== 'https://oauth.telegram.org') return
  try {
    const data = typeof e.data === 'string' ? JSON.parse(e.data) : e.data
    if (data?.event === 'auth_result' && data.result) {
      onTelegramAuth(data.result as TelegramWidgetUser)
    }
  } catch { /* ignore non-JSON messages */ }
}

onMounted(() => {
  // Register global callback (fallback for widget redirect mode)
  ;(window as unknown as Record<string, unknown>)[callbackName] = onTelegramAuth
  window.addEventListener('message', handleMessage)
})

onUnmounted(() => {
  delete (window as unknown as Record<string, unknown>)[callbackName]
  window.removeEventListener('message', handleMessage)
})
</script>

<template>
  <div v-if="botUsername" class="mb-4">
    <button
      type="button"
      class="flex w-full items-center justify-center gap-3 rounded-md border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50"
      :disabled="loading"
      :class="loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'"
      @click="openTelegramAuth"
    >
      <i v-if="!loading" class="pi pi-telegram text-[#2AABEE]" />
      <svg
        v-else
        class="animate-spin"
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
      >
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" class="opacity-25" />
        <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" class="opacity-75" />
      </svg>
      <span>{{ t('auth.telegram.signIn') }}</span>
    </button>
  </div>
</template>
