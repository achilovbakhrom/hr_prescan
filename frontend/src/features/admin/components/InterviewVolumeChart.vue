<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Chart from 'primevue/chart'
import ChartCard from './ChartCard.vue'
import ChartEmpty from './ChartEmpty.vue'
import { chartColors, gridLineColor, monthLabel } from './ChartTheme'
import type { MonthlyInterviewVolume } from '../types/admin.types'

const props = defineProps<{ volume: MonthlyInterviewVolume[] | undefined }>()
const { t } = useI18n()
const c = computed(() => chartColors())

const data = computed(() => {
  if (!props.volume?.length) return null
  return {
    labels: props.volume.map((e) => monthLabel(e.month)),
    datasets: [
      {
        label: t('admin.analytics.interviewVolume'),
        data: props.volume.map((e) => e.count),
        backgroundColor: c.value.accentAi,
        borderColor: c.value.accentAi,
        borderWidth: 1,
        borderRadius: 6,
        barPercentage: 0.6,
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
      ticks: { stepSize: 1, color: c.value.textMuted },
      grid: { color: gridLineColor() },
    },
    x: { ticks: { color: c.value.textMuted }, grid: { display: false } },
  },
}))
</script>

<template>
  <ChartCard :title="t('admin.analytics.interviewVolume')">
    <Chart v-if="data" type="bar" :data="data" :options="options" class="h-full w-full" />
    <ChartEmpty v-else />
  </ChartCard>
</template>
