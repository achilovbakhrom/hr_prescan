<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/features/auth/stores/auth.store'

defineEmits<{
  click: []
}>()

const { t } = useI18n()
const authStore = useAuthStore()

const isCandidate = computed(() => authStore.currentAccessRole === 'candidate')
const label = computed(() =>
  isCandidate.value ? t('aiAssistant.candidateTitle') : t('aiAssistant.hrTitle'),
)
const hint = computed(() =>
  isCandidate.value ? t('aiAssistant.candidateSubtitle') : t('aiAssistant.openHint'),
)
const tooltip = computed(() =>
  isCandidate.value
    ? `${t('aiAssistant.candidateSubtitle')} ${t('aiAssistant.startHintCandidate')}`
    : `${t('aiAssistant.hrSubtitle')} ${t('aiAssistant.startHint')}`,
)
</script>

<template>
  <button
    type="button"
    class="group relative inline-flex h-9 min-w-11 shrink-0 items-center justify-center gap-1 rounded-xl border border-[color:var(--color-border-glass)] bg-white/80 px-2 text-[11px] font-bold text-[color:var(--color-accent)] shadow-sm transition-colors hover:bg-white dark:bg-gray-900/75 dark:text-cyan-300 dark:hover:bg-gray-900 sm:h-11 sm:w-auto sm:gap-2 sm:rounded-2xl sm:border-cyan-300 sm:bg-cyan-600 sm:px-3 sm:text-left sm:text-xs sm:font-semibold sm:text-white sm:shadow-lg sm:shadow-cyan-700/20 sm:hover:-translate-y-0.5 sm:hover:bg-emerald-600 sm:hover:shadow-emerald-700/20 sm:dark:border-cyan-500/60 sm:dark:bg-cyan-600 sm:dark:text-white sm:dark:hover:bg-emerald-600"
    :title="tooltip"
    :aria-label="label"
    @click="$emit('click')"
  >
    <span
      class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-transparent sm:h-8 sm:w-8 sm:rounded-xl sm:bg-white/18 sm:text-white sm:ring-1 sm:ring-white/25"
    >
      <i class="pi pi-bolt text-[13px] sm:text-sm"></i>
    </span>
    <span class="sm:hidden">AI</span>
    <span class="hidden 2xl:block">
      <span class="block leading-4">{{ label }}</span>
      <span class="block max-w-[180px] truncate text-[10px] font-normal text-cyan-50">
        {{ hint }}
      </span>
    </span>
    <span class="hidden sm:inline 2xl:hidden">
      {{ t('aiAssistant.openShortLabel') }}
    </span>
    <span
      class="pointer-events-none absolute right-0 top-[calc(100%+0.5rem)] z-50 hidden w-72 rounded-xl bg-slate-950 px-3 py-2 text-xs font-medium leading-5 text-white shadow-xl sm:group-hover:block"
    >
      {{ tooltip }}
    </span>
  </button>
</template>
