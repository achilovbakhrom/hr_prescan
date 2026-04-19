<script setup lang="ts">
/**
 * HiringFunnel — glass card with stacked stage bars.
 * Uses theme tokens for colors. Data rows sit on solid surface inside card.
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
  const total = props.funnel.total || 1
  const steps = [
    { key: 'applied', count: props.funnel.applied, color: 'var(--color-accent)' },
    { key: 'prescanned', count: props.funnel.prescanned, color: 'var(--color-info)' },
    { key: 'interviewed', count: props.funnel.interviewed, color: 'var(--color-accent-ai)' },
    { key: 'shortlisted', count: props.funnel.shortlisted, color: 'var(--color-warning)' },
    { key: 'hired', count: props.funnel.hired, color: 'var(--color-accent-celebrate)' },
    { key: 'rejected', count: props.funnel.rejected, color: 'var(--color-danger)' },
  ]
  return steps.map((s) => ({
    ...s,
    label: t(`analytics.funnel.${s.key}`),
    pct: Math.round((s.count / total) * 100),
  }))
})
</script>

<template>
  <GlassCard>
    <template #header>
      <h2
        class="text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
      >
        {{ t('analytics.hiringFunnel') }}
      </h2>
    </template>

    <div v-if="funnel && funnel.total > 0" class="flex flex-col gap-4">
      <div v-for="step in funnelSteps" :key="step.key" class="flex flex-col gap-1.5">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-[color:var(--color-text-secondary)]">{{
            step.label
          }}</span>
          <div class="flex items-center gap-2">
            <span
              class="font-mono text-sm font-semibold tabular-nums text-[color:var(--color-text-primary)]"
              >{{ step.count }}</span
            >
            <span class="font-mono text-xs text-[color:var(--color-text-muted)]"
              >({{ step.pct }}%)</span
            >
          </div>
        </div>
        <div class="h-2.5 w-full overflow-hidden rounded-full bg-[color:var(--color-border-soft)]">
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
