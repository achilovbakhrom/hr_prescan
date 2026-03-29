<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'

const { t } = useI18n()

defineProps<{
  prescanUrl: string
  linkCopied: boolean
}>()

const emit = defineEmits<{
  startPrescanning: []
  copyLink: []
}>()
</script>

<template>
  <div class="space-y-4 sm:space-y-6">
    <div class="rounded-lg border border-green-200 bg-green-50 p-3 sm:p-4">
      <div class="flex items-center gap-2">
        <i class="pi pi-check-circle text-green-600"></i>
        <p class="text-sm font-medium text-green-800 sm:text-base">{{ t('candidates.application.success') }}</p>
      </div>
    </div>

    <div class="rounded-lg border border-gray-200 bg-white p-5 text-center sm:p-8">
      <div class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-blue-100 sm:mb-4 sm:h-16 sm:w-16">
        <i class="pi pi-comments text-2xl text-blue-600 sm:text-3xl"></i>
      </div>
      <h2 class="mb-2 text-lg font-bold text-gray-900 sm:text-xl">{{ t('candidates.application.prescanReady') }}</h2>
      <p class="mb-4 text-xs text-gray-500 sm:mb-6 sm:text-sm">{{ t('candidates.application.prescanReadyHint') }}</p>

      <Button :label="t('candidates.application.startPrescanning')" icon="pi pi-play" class="mb-4 w-full" size="large" @click="emit('startPrescanning')" />

      <div class="mb-4 rounded-lg border border-gray-200 bg-gray-50 p-3 sm:mb-6">
        <label class="mb-1 block text-xs font-medium text-gray-500">{{ t('candidates.application.prescanLink') }}</label>
        <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
          <input type="text" readonly :value="prescanUrl" class="w-full rounded border border-gray-200 bg-white px-3 py-2 text-xs text-gray-700 sm:flex-1 sm:text-sm" @focus="($event.target as HTMLInputElement).select()" />
          <Button :label="linkCopied ? t('common.copied') : t('common.copyLink')" :icon="linkCopied ? 'pi pi-check' : 'pi pi-copy'" :severity="linkCopied ? 'success' : 'secondary'" size="small" class="w-full sm:w-auto" @click="emit('copyLink')" />
        </div>
      </div>

      <p class="mb-3 text-xs text-gray-500 sm:mb-4 sm:text-sm">
        <i class="pi pi-envelope mr-1"></i>{{ t('candidates.application.linkSentToEmail') }}
      </p>

      <div class="rounded-lg border border-blue-100 bg-blue-50 p-3 text-left sm:p-4">
        <p class="text-xs text-blue-800 sm:text-sm">
          <i class="pi pi-user-plus mr-1"></i>
          <strong>{{ t('candidates.application.tip') }}:</strong> {{ t('candidates.application.tipText') }}
        </p>
        <RouterLink to="/register" class="mt-2 inline-block text-xs font-medium text-blue-600 hover:underline sm:text-sm">
          {{ t('candidates.application.createAccount') }}
        </RouterLink>
      </div>
    </div>

    <div class="text-center">
      <RouterLink to="/jobs" class="text-xs text-gray-500 hover:text-gray-700 sm:text-sm">
        {{ t('candidates.application.browseMoreJobs') }}
      </RouterLink>
    </div>
  </div>
</template>
