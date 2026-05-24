<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/features/auth/stores/auth.store'

defineEmits<{
  open: []
}>()

const { t } = useI18n()
const authStore = useAuthStore()
const isCandidate = computed(() => authStore.currentAccessRole === 'candidate')

const title = computed(() =>
  isCandidate.value ? t('aiAssistant.candidateTitle') : t('dashboard.ai.title'),
)
const subtitle = computed(() =>
  isCandidate.value ? t('aiAssistant.candidateSubtitle') : t('dashboard.ai.subtitle'),
)
const promptLabel = computed(() =>
  isCandidate.value ? t('aiAssistant.startHintCandidate') : t('aiAssistant.tryAsking'),
)
const prompts = computed(() =>
  isCandidate.value
    ? [
        {
          icon: 'pi pi-search',
          label: t('aiAssistant.suggestions.searchJobs.title'),
        },
        {
          icon: 'pi pi-file-edit',
          label: t('aiAssistant.suggestions.improveCv.title'),
        },
      ]
    : [
        {
          icon: 'pi pi-users',
          label: t('dashboard.ai.placeholder'),
        },
        {
          icon: 'pi pi-chart-line',
          label: t('aiAssistant.suggestions.analytics.title'),
        },
      ],
)
</script>

<template>
  <div
    class="rounded-lg border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-raised)] p-5"
  >
    <div class="flex items-start gap-3">
      <span
        class="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]"
      >
        <i class="pi pi-comments text-base"></i>
      </span>
      <div>
        <p class="text-xs font-semibold uppercase text-[color:var(--color-accent)]">
          {{ t('aiAssistant.openLabel') }}
        </p>
        <h2 class="mt-1 text-xl font-semibold text-[color:var(--color-text-primary)]">
          {{ title }}
        </h2>
      </div>
    </div>
    <p class="mt-3 text-sm leading-relaxed text-[color:var(--color-text-secondary)]">
      {{ subtitle }}
    </p>
    <p class="mt-4 text-xs font-semibold text-[color:var(--color-text-muted)]">
      {{ promptLabel }}
    </p>
    <button
      v-for="prompt in prompts"
      :key="prompt.label"
      type="button"
      class="mt-2 flex w-full cursor-pointer items-center justify-between rounded-lg border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface)] px-4 py-3 text-left text-sm text-[color:var(--color-text-secondary)] transition-colors hover:border-[color:var(--color-accent)] hover:bg-[color:var(--color-accent-soft)] hover:text-[color:var(--color-text-primary)]"
      @click="$emit('open')"
    >
      <span class="flex min-w-0 items-center gap-2">
        <i :class="prompt.icon" class="text-[color:var(--color-accent)]"></i>
        <span class="truncate">{{ prompt.label }}</span>
      </span>
      <i class="pi pi-arrow-right text-xs text-[color:var(--color-text-muted)]"></i>
    </button>
    <button
      type="button"
      class="mt-4 w-full rounded-lg bg-[color:var(--color-accent)] px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-[color:var(--color-accent-hover)]"
      @click="$emit('open')"
    >
      {{ t('aiAssistant.openCta') }}
    </button>
  </div>
</template>
