<script setup lang="ts">
import Tag from 'primevue/tag'
import type { ApplicationStatus } from '../types/candidate.types'

defineProps<{
  status: ApplicationStatus
}>()

const STATUS_CONFIG: Record<
  ApplicationStatus,
  { label: string; severity: string }
> = {
  applied: { label: 'Applied', severity: 'info' },
  interview_scheduled: { label: 'Interview Scheduled', severity: 'warn' },
  interview_in_progress: { label: 'Interview In Progress', severity: 'warn' },
  interview_completed: { label: 'Interview Completed', severity: 'success' },
  reviewing: { label: 'Reviewing', severity: 'warn' },
  shortlisted: { label: 'Shortlisted', severity: 'success' },
  rejected: { label: 'Rejected', severity: 'danger' },
}
</script>

<template>
  <Tag
    :value="STATUS_CONFIG[status].label"
    :severity="STATUS_CONFIG[status].severity"
  />
</template>
