<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'

const props = defineProps<{
  prescanUrl: string
  linkCopied: boolean
  telegramCode?: number | null
}>()

const emit = defineEmits<{
  startPrescanning: []
  copyLink: []
}>()

const { t } = useI18n()

const telegramBotUsername = (import.meta.env.VITE_TELEGRAM_CANDIDATE_BOT_USERNAME as string | undefined) ?? ''

const telegramDeepLink = computed(() => {
  if (!telegramBotUsername || !props.telegramCode) return ''
  return `https://t.me/${telegramBotUsername}?start=vac_${props.telegramCode}`
})

const telegramCopied = ref(false)

async function copyTelegramLink(): Promise<void> {
  if (!telegramDeepLink.value) return
  try {
    await navigator.clipboard.writeText(telegramDeepLink.value)
    telegramCopied.value = true
    setTimeout(() => {
      telegramCopied.value = false
    }, 2000)
  } catch {
    /* clipboard unavailable; user can copy manually */
  }
}
</script>

<template>
  <div class="space-y-4 sm:space-y-6">
    <div class="rounded-lg border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950 p-3 sm:p-4">
      <div class="flex items-center gap-2">
        <i class="pi pi-check-circle text-green-600"></i>
        <p class="text-sm font-medium text-green-800 sm:text-base">
          {{ t('candidates.application.success') }}
        </p>
      </div>
    </div>

    <div class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 text-center sm:p-8">
      <div
        class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-950 sm:mb-4 sm:h-16 sm:w-16"
      >
        <i class="pi pi-comments text-2xl text-blue-600 dark:text-blue-400 sm:text-3xl"></i>
      </div>
      <h2 class="mb-2 text-lg font-bold text-gray-900 dark:text-white sm:text-xl">
        {{ t('candidates.application.prescanReady') }}
      </h2>
      <p class="mb-4 text-xs text-gray-500 dark:text-gray-400 sm:mb-6 sm:text-sm">
        {{ t('candidates.application.prescanReadyHint') }}
      </p>

      <Button
        :label="t('candidates.application.startPrescanning')"
        icon="pi pi-play"
        class="mb-4 w-full"
        size="large"
        @click="emit('startPrescanning')"
      />

      <div class="mb-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 p-3 sm:mb-6">
        <label class="mb-1 block text-xs font-medium text-gray-500">{{
          t('candidates.application.prescanLink')
        }}</label>
        <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
          <input
            type="text"
            readonly
            :value="prescanUrl"
            class="w-full rounded border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-xs text-gray-700 dark:text-gray-300 sm:flex-1 sm:text-sm"
            @focus="($event.target as HTMLInputElement).select()"
          />
          <Button
            :label="linkCopied ? t('common.copied') : t('common.copyLink')"
            :icon="linkCopied ? 'pi pi-check' : 'pi pi-copy'"
            :severity="linkCopied ? 'success' : 'secondary'"
            size="small"
            class="w-full sm:w-auto"
            @click="emit('copyLink')"
          />
        </div>
      </div>

      <p class="mb-3 text-xs text-gray-500 dark:text-gray-400 sm:mb-4 sm:text-sm">
        <i class="pi pi-envelope mr-1"></i>{{ t('candidates.application.linkSentToEmail') }}
      </p>

      <div
        v-if="telegramDeepLink"
        class="mb-4 rounded-lg border border-sky-200 bg-sky-50 p-3 text-left sm:mb-6 sm:p-4"
      >
        <div class="mb-2 flex items-center gap-2">
          <i class="pi pi-telegram text-sky-600"></i>
          <p class="text-xs font-semibold text-sky-900 sm:text-sm">
            {{ t('candidates.application.telegramOption') }}
          </p>
        </div>
        <p class="mb-3 text-xs text-sky-800 sm:text-sm">
          {{ t('candidates.application.telegramOptionHint') }}
        </p>
        <div class="flex flex-col gap-2 sm:flex-row">
          <Button
            as="a"
            :href="telegramDeepLink"
            target="_blank"
            rel="noopener"
            :label="t('candidates.application.openInTelegram')"
            icon="pi pi-external-link"
            size="small"
            class="w-full sm:w-auto"
          />
          <Button
            :label="telegramCopied ? t('common.copied') : t('candidates.application.copyTelegramLink')"
            :icon="telegramCopied ? 'pi pi-check' : 'pi pi-copy'"
            :severity="telegramCopied ? 'success' : 'secondary'"
            size="small"
            class="w-full sm:w-auto"
            @click="copyTelegramLink"
          />
        </div>
      </div>

      <div class="rounded-lg border border-blue-100 dark:border-blue-900 bg-blue-50 dark:bg-blue-950 p-3 text-left sm:p-4">
        <p class="text-xs text-blue-800 dark:text-blue-200 sm:text-sm">
          <i class="pi pi-user-plus mr-1"></i>
          <strong>{{ t('candidates.application.tip') }}:</strong>
          {{ t('candidates.application.tipText') }}
        </p>
        <RouterLink
          to="/register"
          class="mt-2 inline-block text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline sm:text-sm"
        >
          {{ t('candidates.application.createAccount') }}
        </RouterLink>
      </div>
    </div>

    <div class="text-center">
      <RouterLink to="/jobs" class="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 sm:text-sm">
        {{ t('candidates.application.browseMoreJobs') }}
      </RouterLink>
    </div>
  </div>
</template>
