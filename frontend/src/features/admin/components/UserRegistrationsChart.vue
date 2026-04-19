<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Chart from 'primevue/chart'
import ChartCard from './ChartCard.vue'
import ChartEmpty from './ChartEmpty.vue'
import { chartColors, gridLineColor, monthLabel } from './ChartTheme'
import type { MonthlyRegistration } from '../types/admin.types'

const props = defineProps<{ registrations: MonthlyRegistration[] | undefined }>()
const { t } = useI18n()
const c = computed(() => chartColors())

const data = computed(() => {
  if (!props.registrations?.length) return null
  const mm = new Map<string, Record<string, number>>()
  for (const e of props.registrations) {
    if (!mm.has(e.month)) mm.set(e.month, {})
    mm.get(e.month)![e.role] = e.count
  }
  const months = Array.from(mm.keys()).sort()
  const rc: Record<string, { bg: string; label: string }> = {
    candidate: { bg: c.value.accent, label: t('admin.analytics.candidates') },
    hr: { bg: c.value.success, label: t('admin.analytics.hrManagers') },
    admin: { bg: c.value.warning, label: t('admin.analytics.admins') },
  }
  return {
    labels: months.map(monthLabel),
    datasets: ['candidate', 'hr', 'admin'].map((r) => ({
      label: rc[r]?.label || r,
      data: months.map((m) => mm.get(m)?.[r] || 0),
      backgroundColor: rc[r]?.bg,
      borderWidth: 0,
      borderRadius: 4,
      barPercentage: 0.7,
    })),
  }
})
const options = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: {
        color: c.value.textSecondary,
        usePointStyle: true,
        pointStyle: 'circle',
        padding: 12,
      },
    },
  },
  scales: {
    x: {
      stacked: true,
      ticks: { color: c.value.textMuted },
      grid: { display: false },
    },
    y: {
      stacked: true,
      beginAtZero: true,
      ticks: { stepSize: 1, color: c.value.textMuted },
      grid: { color: gridLineColor() },
    },
  },
}))
</script>

<template>
  <ChartCard :title="t('admin.analytics.userRegistrations')">
    <Chart v-if="data" type="bar" :data="data" :options="options" class="h-full w-full" />
    <ChartEmpty v-else />
  </ChartCard>
</template>
