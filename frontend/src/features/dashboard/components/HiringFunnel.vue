<script setup lang="ts">
/**
 * HiringFunnel — Figma dashboard rail card.
 * Four stages (Applied → Prescreened → Interviewed → Shortlisted) with a thin
 * colored progress bar (width = count / applied) and the raw count on the right.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import GlassCard from '@/shared/components/GlassCard.vue'

const props = defineProps<{
  funnel: {
    total: number
    applied: number
    prescanned: number
    interviewed: number
    shortlisted: number
    hired: number
    rejected: number
  } | null
}>()

const { t } = useI18n()

const funnelSteps = computed(() => {
  if (!props.funnel) return []
  const base = props.funnel.applied || props.funnel.total || 1
  const steps = [
    { key: 'applied', count: props.funnel.applied, color: 'var(--color-accent)' },
    { key: 'prescanned', count: props.funnel.prescanned, color: '#a855f7' },
    { key: 'interviewed', count: props.funnel.interviewed, color: 'var(--color-accent-celebrate)' },
    { key: 'shortlisted', count: props.funnel.shortlisted, color: '#2dd4bf' },
  ]
  return steps.map((s) => ({
    ...s,
    label: t(`analytics.funnel.${s.key}`),
    pct: Math.round((s.count / base) * 100),
  }))
})
</script>

<template>
  <GlassCard>
    <template #header>
      <h3 class="text-base font-semibold text-[color:var(--color-text-primary)]">
        {{ t('analytics.hiringFunnel') }}
      </h3>
    </template>

    <div v-if="funnel && funnel.total > 0" class="flex flex-col gap-5">
      <div v-for="step in funnelSteps" :key="step.key" class="flex flex-col gap-2">
        <div class="flex items-center justify-between">
          <span class="text-sm text-[color:var(--color-text-secondary)]">{{ step.label }}</span>
          <span
            class="font-mono text-sm font-semibold tabular-nums text-[color:var(--color-text-primary)]"
            >{{ step.count }}</span
          >
        </div>
        <div class="h-2 w-full overflow-hidden rounded-full bg-[color:var(--color-surface-sunken)]">
          <div
            class="h-full rounded-full transition-all duration-500 ease-ios"
            :style="{ width: `${Math.max(step.pct, 2)}%`, backgroundColor: step.color }"
          ></div>
        </div>
      </div>
    </div>
    <div
      v-else
      class="flex flex-col items-center py-8 text-center text-[color:var(--color-text-muted)]"
    >
      <i class="pi pi-chart-bar mb-2 text-2xl"></i>
      <p class="text-sm">{{ t('analytics.noData') }}</p>
    </div>
  </GlassCard>
</template>
