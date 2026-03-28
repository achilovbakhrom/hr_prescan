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
const widgetContainer = ref<HTMLElement | null>(null)
const loading = ref(false)
const ready = ref(false)

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

onMounted(() => {
  if (!botUsername || !widgetContainer.value) return

  ;(window as Record<string, unknown>)[callbackName] = onTelegramAuth

  const script = document.createElement('script')
  script.async = true
  script.src = 'https://telegram.org/js/telegram-widget.js?22'
  script.setAttribute('data-telegram-login', botUsername)
  script.setAttribute('data-size', 'large')
  script.setAttribute('data-radius', '6')
  script.setAttribute('data-request-access', 'write')
  script.setAttribute('data-userpic', 'false')
  script.setAttribute('data-onauth', `${callbackName}(user)`)
  script.onload = () => {
    ready.value = true
  }

  widgetContainer.value.appendChild(script)
})

onUnmounted(() => {
  delete (window as Record<string, unknown>)[callbackName]
})
</script>

<template>
  <div v-if="botUsername" class="relative mb-4">
    <!-- Visual button the user sees -->
    <div
      class="flex w-full items-center justify-center gap-3 rounded-md border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm"
      :class="loading ? 'opacity-50' : ''"
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
    </div>

    <!-- Invisible Telegram iframe overlay — real click target -->
    <div
      ref="widgetContainer"
      class="absolute inset-0 flex items-center justify-center overflow-hidden"
      :class="loading ? 'pointer-events-none' : ''"
      :style="{ opacity: ready ? '0.01' : '0' }"
    />
  </div>
</template>

<style scoped>
:deep(iframe) {
  width: 100% !important;
  height: 100% !important;
  cursor: pointer;
}
</style>
