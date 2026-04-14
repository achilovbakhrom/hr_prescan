<script setup lang="ts">
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

const severity = computed(() => {
  if (percentage.value >= 90) return 'danger'
  if (percentage.value >= 70) return 'warning'
  return 'info'
})

const colorClass = computed(() => {
  if (severity.value === 'danger') return 'text-red-600'
  if (severity.value === 'warning') return 'text-yellow-600'
  return 'text-blue-600'
})

const displayUsed = computed(() => {
  return props.unit ? `${props.used} ${props.unit}` : String(props.used)
})

const displayLimit = computed(() => {
  return props.unit ? `${props.limit} ${props.unit}` : String(props.limit)
})
</script>

<template>
  <div class="space-y-1">
    <div class="flex items-center justify-between text-sm">
      <span class="font-medium text-gray-700">{{ label }}</span>
      <span :class="colorClass"> {{ displayUsed }} / {{ displayLimit }} </span>
    </div>
    <ProgressBar
      :value="percentage"
      :show-value="false"
      style="height: 8px"
      :class="
        severity === 'danger'
          ? '[&_.p-progressbar-value]:!bg-red-500'
          : severity === 'warning'
            ? '[&_.p-progressbar-value]:!bg-yellow-500'
            : ''
      "
    />
  </div>
</template>
