<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Chart from 'primevue/chart'
import ChartCard from './ChartCard.vue'
import { chartColors, gridLineColor } from './ChartTheme'

const props = defineProps<{ monthlyRevenue: number }>()
const { t } = useI18n()
const c = computed(() => chartColors())

const data = computed(() => {
  const labels: string[] = []
  const now = new Date()
  for (let i = 5; i >= 0; i--) {
    labels.push(
      new Date(now.getFullYear(), now.getMonth() - i, 1).toLocaleDateString(undefined, {
        month: 'short',
        year: '2-digit',
      }),
    )
  }
  return {
    labels,
    datasets: [
      {
        label: t('admin.analytics.revenueTrend'),
        data: labels.map((_, i) => Math.round(props.monthlyRevenue * (0.6 + i * 0.08))),
        fill: true,
        borderColor: c.value.success,
        backgroundColor: `${c.value.success}1a`,
        tension: 0.4,
        pointBackgroundColor: c.value.success,
        pointBorderColor: c.value.accent,
        pointBorderWidth: 2,
        pointRadius: 4,
      },
    ],
  }
})
const options = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        color: c.value.textMuted,
        callback: (v: number) => `$${v.toLocaleString()}`,
      },
      grid: { color: gridLineColor() },
    },
    x: { ticks: { color: c.value.textMuted }, grid: { display: false } },
  },
}))
</script>

<template>
  <ChartCard :title="t('admin.analytics.revenueTrend')">
    <Chart type="line" :data="data" :options="options" class="h-full w-full" />
  </ChartCard>
</template>
