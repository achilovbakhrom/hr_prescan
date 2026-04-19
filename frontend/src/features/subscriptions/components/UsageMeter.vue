<script setup lang="ts">
/**
 * UsageMeter — labeled progress meter for a subscription quota.
 * Uses design tokens for colors. Severity shifts at 70% / 90%.
 */
import { computed } from 'vue'
import ProgressBar from 'primevue/progressbar'

const props = defineProps<{
  label: string
  used: number
  limit: number
  unit?: string
}>()

const percentage = computed(() => {
  if (props.limit === 0) return 0
  return Math.min(Math.round((props.used / props.limit) * 100), 100)
})

const severity = computed<'info' | 'warning' | 'danger'>(() => {
  if (percentage.value >= 90) return 'danger'
  if (percentage.value >= 70) return 'warning'
  return 'info'
})

const valueColor = computed(() => {
  if (severity.value === 'danger') return 'text-[color:var(--color-danger)]'
  if (severity.value === 'warning') return 'text-[color:var(--color-warning)]'
  return 'text-[color:var(--color-accent)]'
})

const barColorClass = computed(() => {
  if (severity.value === 'danger') return 'usage-meter--danger'
  if (severity.value === 'warning') return 'usage-meter--warning'
  return 'usage-meter--info'
})

const displayUsed = computed(() =>
  props.unit ? `${props.used} ${props.unit}` : String(props.used),
)

const displayLimit = computed(() =>
  props.unit ? `${props.limit} ${props.unit}` : String(props.limit),
)
</script>

<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between text-sm">
      <span class="font-medium text-[color:var(--color-text-secondary)]">{{ label }}</span>
      <span class="font-mono text-xs font-semibold" :class="valueColor">
        {{ displayUsed }} / {{ displayLimit }}
      </span>
    </div>
    <ProgressBar
      :value="percentage"
      :show-value="false"
      :class="['usage-meter', barColorClass]"
      style="height: 8px"
    />
  </div>
</template>

<style scoped>
.usage-meter :deep(.p-progressbar-value) {
  transition:
    width 480ms var(--ease-ios),
    background-color 240ms var(--ease-ios);
}
.usage-meter--info :deep(.p-progressbar-value) {
  background: var(--color-accent) !important;
}
.usage-meter--warning :deep(.p-progressbar-value) {
  background: var(--color-warning) !important;
}
.usage-meter--danger :deep(.p-progressbar-value) {
  background: var(--color-danger) !important;
}
</style>
