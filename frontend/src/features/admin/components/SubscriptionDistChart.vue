<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Chart from 'primevue/chart'
import ChartCard from './ChartCard.vue'
import ChartEmpty from './ChartEmpty.vue'
import { chartColors, tierColor } from './ChartTheme'
import type { SubscriptionDistribution } from '../types/admin.types'

const props = defineProps<{ distribution: SubscriptionDistribution[] | undefined }>()
const { t } = useI18n()
const c = computed(() => chartColors())

const data = computed(() => {
  if (!props.distribution?.length) return null
  const colors = props.distribution.map((e) => tierColor(e.tier))
  return {
    labels: props.distribution.map((e) => e.name || e.tier),
    datasets: [
      {
        data: props.distribution.map((e) => e.count),
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: c.value.textSecondary,
      },
    ],
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
  cutout: '60%',
}))
</script>

<template>
  <ChartCard :title="t('admin.analytics.subscriptionDistribution')">
    <Chart v-if="data" type="doughnut" :data="data" :options="options" class="h-full w-full" />
    <ChartEmpty v-else />
  </ChartCard>
</template>
