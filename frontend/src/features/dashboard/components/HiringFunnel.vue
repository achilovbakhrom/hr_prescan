<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
  funnel: { total: number; applied: number; prescanned: number; interviewed: number; shortlisted: number; hired: number; rejected: number } | null
}>()

const funnelSteps = computed(() => {
  if (!props.funnel) return []
  const total = props.funnel.total || 1
  const steps = [
    { key: 'applied', count: props.funnel.applied, color: 'bg-blue-500' },
    { key: 'prescanned', count: props.funnel.prescanned, color: 'bg-cyan-500' },
    { key: 'interviewed', count: props.funnel.interviewed, color: 'bg-violet-500' },
    { key: 'shortlisted', count: props.funnel.shortlisted, color: 'bg-amber-500' },
    { key: 'hired', count: props.funnel.hired, color: 'bg-emerald-500' },
    { key: 'rejected', count: props.funnel.rejected, color: 'bg-red-500' },
  ]
  return steps.map(s => ({ ...s, label: t(`analytics.funnel.${s.key}`), pct: Math.round((s.count / total) * 100) }))
})
</script>

<template>
  <div class="rounded-xl border border-gray-100 bg-white p-6">
    <h2 class="mb-5 text-sm font-semibold uppercase tracking-wider text-gray-400">{{ t('analytics.hiringFunnel') }}</h2>
    <div v-if="funnel && funnel.total > 0" class="space-y-4">
      <div v-for="step in funnelSteps" :key="step.key" class="space-y-1.5">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700">{{ step.label }}</span>
          <div class="flex items-center gap-2">
            <span class="text-sm font-semibold text-gray-900">{{ step.count }}</span>
            <span class="text-xs text-gray-400">({{ step.pct }}%)</span>
          </div>
        </div>
        <div class="h-2.5 w-full overflow-hidden rounded-full bg-gray-100">
          <div class="h-full rounded-full transition-all duration-500" :class="step.color" :style="{ width: `${Math.max(step.pct, 2)}%` }"></div>
        </div>
      </div>
    </div>
    <div v-else class="flex flex-col items-center py-8 text-center">
      <div class="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100"><i class="pi pi-chart-bar text-xl text-gray-400"></i></div>
      <p class="mt-3 text-sm text-gray-500">{{ t('analytics.noData') }}</p>
    </div>
  </div>
</template>
