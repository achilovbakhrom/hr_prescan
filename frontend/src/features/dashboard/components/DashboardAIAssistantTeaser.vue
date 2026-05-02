<script setup lang="ts">
/**
 * DashboardAIAssistantTeaser — rail card with violet AI accent.
 * Uses GlassCard accent="ai" + small Prism glyph + CTA.
 *
 * Spec: docs/design/spec.md §9 (dashboard rail).
 */
import { useI18n } from 'vue-i18n'
import GlassCard from '@/shared/components/GlassCard.vue'
import AppLogo from '@/shared/components/AppLogo.vue'

defineEmits<{ (e: 'open'): void }>()

const { t } = useI18n()
</script>

<template>
  <GlassCard accent="ai" class="relative overflow-hidden">
    <div class="relative z-10 flex flex-col gap-3">
      <div class="flex items-center gap-2">
        <AppLogo variant="glyph" size="sm" :linked="false" />
        <span
          class="font-mono text-[10px] font-semibold uppercase tracking-widest text-[color:var(--color-accent-ai)]"
          >{{ t('aiAssistant.title') }}</span
        >
      </div>
      <h3 class="text-base font-semibold text-[color:var(--color-text-primary)]">
        {{ t('dashboard.ai.title') }}
      </h3>
      <p class="text-sm text-[color:var(--color-text-secondary)]">
        {{ t('dashboard.ai.subtitle') }}
      </p>
      <button
        type="button"
        class="mt-2 flex cursor-pointer items-center justify-between gap-3 rounded-[--radius-sm] border border-[color:var(--color-border-glass)] bg-[color:var(--color-surface-raised)] px-3 py-2 text-left text-sm text-[color:var(--color-text-muted)] transition-colors hover:border-[color:var(--color-accent-ai)] hover:text-[color:var(--color-text-primary)] dark:border-violet-300/20 dark:bg-violet-300/10 dark:text-slate-200 dark:hover:border-violet-300/45 dark:hover:bg-violet-300/15"
        @click="$emit('open')"
      >
        <span class="flex items-center gap-2">
          <i class="pi pi-sparkles text-[color:var(--color-accent-ai)]"></i>
          <span>{{ t('dashboard.ai.placeholder') }}</span>
        </span>
        <span class="font-mono text-[10px] text-[color:var(--color-text-muted)]" aria-hidden="true"
          >⌘K</span
        >
      </button>
    </div>
  </GlassCard>
</template>
