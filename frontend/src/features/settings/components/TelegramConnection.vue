<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { settingsService } from '../services/settings.service'

const emit = defineEmits<{
  error: [msg: string]
  success: [msg: string]
}>()

const { t } = useI18n()

const telegramLinked = ref(false)
const telegramUsername = ref('')
const telegramLinkUrl = ref('')
const generatingCode = ref(false)

async function loadStatus(): Promise<void> {
  try {
    const status = await settingsService.getTelegramStatus()
    telegramLinked.value = status.linked
    telegramUsername.value = status.telegramUsername ?? ''
    if (status.linked) {
      telegramLinkUrl.value = ''
    }
  } catch {
    /* silent */
  }
}

function handleWindowFocus(): void {
  void loadStatus()
}

onMounted(() => {
  void loadStatus()
  window.addEventListener('focus', handleWindowFocus)
})

onBeforeUnmount(() => {
  window.removeEventListener('focus', handleWindowFocus)
})

async function handleGenerateCode(): Promise<void> {
  generatingCode.value = true
  try {
    const result = await settingsService.generateTelegramLinkCode()
    telegramLinkUrl.value = result.linkUrl
  } catch {
    emit('error', t('telegram.generateLinkError'))
  } finally {
    generatingCode.value = false
  }
}

async function handleUnlink(): Promise<void> {
  try {
    await settingsService.unlinkTelegram()
    telegramLinked.value = false
    telegramUsername.value = ''
    telegramLinkUrl.value = ''
    emit('success', t('telegram.disconnected'))
  } catch {
    emit('error', t('telegram.disconnectError'))
  }
}
</script>

<template>
  <div class="rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-800">
    <div class="mb-4 flex items-center gap-3">
      <div
        class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-500/10"
      >
        <i class="pi pi-send text-lg text-blue-500"></i>
      </div>
      <div>
        <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-100">
          {{ t('telegram.title') }}
        </h3>
        <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('telegram.subtitle') }}</p>
      </div>
    </div>

    <div v-if="telegramLinked" class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
        <span class="text-sm text-gray-700 dark:text-gray-200"
          >{{ t('telegram.connected') }}: @{{ telegramUsername }}</span
        >
      </div>
      <Button
        :label="t('telegram.disconnect')"
        severity="danger"
        text
        size="small"
        @click="handleUnlink"
      />
    </div>

    <div v-else>
      <div v-if="telegramLinkUrl" class="text-center">
        <p class="mb-3 text-sm text-gray-600 dark:text-gray-300">
          {{ t('telegram.deepLinkHint') }}
        </p>
        <a
          :href="telegramLinkUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="mb-3 inline-flex items-center gap-2 rounded-xl bg-blue-500 px-6 py-3 font-semibold text-white transition-colors hover:bg-blue-600"
        >
          <i class="pi pi-send"></i>{{ t('telegram.openBot') }}
        </a>
        <p class="text-xs text-gray-400 dark:text-gray-500">{{ t('telegram.linkCodeExpires') }}</p>
      </div>
      <div v-else class="text-center">
        <p class="mb-3 text-sm text-gray-500 dark:text-gray-400">
          {{ t('telegram.notConnected') }}
        </p>
        <Button
          :label="t('telegram.connect')"
          icon="pi pi-link"
          size="small"
          :loading="generatingCode"
          @click="handleGenerateCode"
        />
      </div>
    </div>
  </div>
</template>
