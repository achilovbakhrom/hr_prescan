<script setup lang="ts">
import { useI18n } from 'vue-i18n'

defineEmits<{
  open: []
}>()

const { t } = useI18n()
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
          {{ t('dashboard.ai.title') }}
        </h2>
      </div>
    </div>
    <p class="mt-3 text-sm leading-relaxed text-[color:var(--color-text-secondary)]">
      {{ t('dashboard.ai.subtitle') }}
    </p>
    <p class="mt-4 text-xs font-semibold text-[color:var(--color-text-muted)]">
      {{ t('aiAssistant.tryAsking') }}
    </p>
    <button
      type="button"
      class="mt-2 flex w-full cursor-pointer items-center justify-between rounded-lg border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface)] px-4 py-3 text-left text-sm text-[color:var(--color-text-secondary)] transition-colors hover:border-[color:var(--color-accent)] hover:bg-[color:var(--color-accent-soft)] hover:text-[color:var(--color-text-primary)]"
      @click="$emit('open')"
    >
      <span class="flex min-w-0 items-center gap-2">
        <i class="pi pi-users text-[color:var(--color-accent)]"></i>
        <span class="truncate">{{ t('dashboard.ai.placeholder') }}</span>
      </span>
      <i class="pi pi-arrow-right text-xs text-[color:var(--color-text-muted)]"></i>
    </button>
    <button
      type="button"
      class="mt-2 flex w-full cursor-pointer items-center justify-between rounded-lg border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface)] px-4 py-3 text-left text-sm text-[color:var(--color-text-secondary)] transition-colors hover:border-[color:var(--color-accent)] hover:bg-[color:var(--color-accent-soft)] hover:text-[color:var(--color-text-primary)]"
      @click="$emit('open')"
    >
      <span class="flex min-w-0 items-center gap-2">
        <i class="pi pi-chart-line text-[color:var(--color-accent)]"></i>
        <span class="truncate">{{ t('aiAssistant.suggestions.analytics.title') }}</span>
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
