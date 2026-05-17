<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'

defineProps<{
  title: string
  subtitle: string
}>()

defineEmits<{
  clear: []
  close: []
}>()

const { t } = useI18n()
</script>

<template>
  <header
    class="border-b border-cyan-100 bg-[linear-gradient(135deg,#ecfeff_0%,#f0fdf4_46%,#fffbeb_100%)] px-4 py-4 dark:border-slate-800 dark:bg-[linear-gradient(135deg,#082f49_0%,#052e2b_54%,#422006_100%)] sm:px-6"
  >
    <div class="flex items-start justify-between gap-4">
      <div class="flex min-w-0 items-start gap-3">
        <span
          class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-cyan-600 text-white shadow-lg shadow-cyan-600/25"
        >
          <i class="pi pi-comments text-lg"></i>
        </span>
        <div class="min-w-0">
          <p class="text-xs font-semibold uppercase text-cyan-700 dark:text-cyan-200">
            {{ t('aiAssistant.title') }}
          </p>
          <h2 class="mt-1 text-xl font-semibold text-slate-950 dark:text-white">
            {{ title }}
          </h2>
          <p class="mt-1 max-w-2xl text-sm leading-6 text-slate-700 dark:text-slate-200">
            {{ subtitle }}
          </p>
        </div>
      </div>
      <div class="flex shrink-0 items-center gap-1">
        <Button
          type="button"
          icon="pi pi-trash"
          severity="secondary"
          text
          rounded
          size="small"
          :title="t('aiAssistant.clearHistory')"
          @click="$emit('clear')"
        />
        <Button
          type="button"
          icon="pi pi-times"
          severity="secondary"
          text
          rounded
          size="small"
          :aria-label="t('common.close')"
          @click="$emit('close')"
        />
      </div>
    </div>
  </header>
</template>
