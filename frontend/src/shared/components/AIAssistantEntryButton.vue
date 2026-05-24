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
    class="group relative flex h-10 w-10 items-center justify-center gap-2 rounded-2xl border border-cyan-300 bg-cyan-600 text-left text-xs font-semibold text-white shadow-lg shadow-cyan-700/20 transition-all hover:-translate-y-0.5 hover:bg-emerald-600 hover:shadow-emerald-700/20 dark:border-cyan-500/60 dark:bg-cyan-600 dark:hover:bg-emerald-600 sm:h-11 sm:w-auto sm:px-3"
    :title="tooltip"
    :aria-label="label"
    @click="$emit('click')"
  >
    <span
      class="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-white/18 text-white ring-1 ring-white/25"
    >
      <i class="pi pi-bolt text-sm"></i>
    </span>
    <span class="hidden 2xl:block">
      <span class="block leading-4">{{ label }}</span>
      <span class="block max-w-[180px] truncate text-[10px] font-normal text-cyan-50">
        {{ hint }}
      </span>
    </span>
    <i class="pi pi-info-circle hidden text-xs text-cyan-50/90 2xl:block"></i>
    <span class="hidden sm:inline 2xl:hidden">
      {{ t('aiAssistant.openShortLabel') }}
    </span>
    <span
      class="pointer-events-none absolute right-0 top-[calc(100%+0.5rem)] z-50 hidden w-72 rounded-xl bg-slate-950 px-3 py-2 text-xs font-medium leading-5 text-white shadow-xl group-hover:block"
    >
      {{ tooltip }}
    </span>
  </button>
</template>
