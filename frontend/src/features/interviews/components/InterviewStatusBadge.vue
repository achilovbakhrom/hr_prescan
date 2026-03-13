<script setup lang="ts">
import Tag from 'primevue/tag'
import type { InterviewStatus } from '../types/interview.types'

const props = defineProps<{
  status: InterviewStatus
}>()

const statusConfig: Record<
  InterviewStatus,
  { label: string; severity: 'success' | 'info' | 'warn' | 'danger' | 'secondary' }
> = {
  scheduled: { label: 'Scheduled', severity: 'info' },
  in_progress: { label: 'In Progress', severity: 'warn' },
  completed: { label: 'Completed', severity: 'success' },
  cancelled: { label: 'Cancelled', severity: 'danger' },
  no_show: { label: 'No Show', severity: 'secondary' },
}

const config = statusConfig[props.status] ?? { label: props.status, severity: 'secondary' as const }
</script>

<template>
  <Tag :value="config.label" :severity="config.severity" />
</template>
