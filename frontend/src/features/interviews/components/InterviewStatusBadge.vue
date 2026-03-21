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
  pending: { label: 'Pending', severity: 'warn' },
  in_progress: { label: 'In Progress', severity: 'info' },
  completed: { label: 'Completed', severity: 'success' },
  cancelled: { label: 'Cancelled', severity: 'danger' },
  expired: { label: 'Expired', severity: 'secondary' },
}

const config = statusConfig[props.status] ?? { label: props.status, severity: 'secondary' as const }
</script>

<template>
  <Tag :value="config.label" :severity="config.severity" />
</template>
