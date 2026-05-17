<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import DashboardStatsCard from './DashboardStatsCard.vue'
import type { ProcessMetrics } from '../types/analytics.types'

const props = defineProps<{
  metrics: ProcessMetrics | null
}>()

const { t } = useI18n()

function valueOrZero(value: number | undefined): number {
  return value ?? 0
}

function formatDays(value: number | string | null | undefined): string {
  if (value === null || value === undefined || value === '') return '-'
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) return '-'
  return `${numeric.toFixed(1)} ${t('analytics.days')}`
}
</script>

<template>
  <section class="mb-6">
    <div class="mb-3 flex items-center justify-between gap-3">
      <h2
        class="text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
      >
        {{ t('analytics.processHealth') }}
      </h2>
    </div>
    <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
      <DashboardStatsCard
        icon="pi pi-briefcase"
        icon-accent="info"
        :label="t('analytics.activeVacancies')"
        :value="valueOrZero(props.metrics?.activeVacancies)"
      />
      <DashboardStatsCard
        icon="pi pi-clock"
        icon-accent="ai"
        :label="t('analytics.pendingInterviews')"
        :value="valueOrZero(props.metrics?.pendingInterviews)"
      />
      <DashboardStatsCard
        icon="pi pi-exclamation-circle"
        icon-accent="warning"
        :label="t('analytics.staleApplications')"
        :value="valueOrZero(props.metrics?.staleApplications)"
      />
      <DashboardStatsCard
        icon="pi pi-calendar"
        icon-accent="success"
        :label="t('analytics.avgDecisionDays')"
        :value="formatDays(props.metrics?.averageDecisionDays)"
      />
    </div>
  </section>
</template>
