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
  prescanned: { label: 'Prescanned', severity: 'info' },
  interviewed: { label: 'Interviewed', severity: 'success' },
  shortlisted: { label: 'Shortlisted', severity: 'success' },
  hired: { label: 'Hired', severity: 'success' },
  rejected: { label: 'Rejected', severity: 'danger' },
  expired: { label: 'Expired', severity: 'secondary' },
  archived: { label: 'Archived', severity: 'secondary' },
}
</script>

<template>
  <Tag
    :value="STATUS_CONFIG[status].label"
    :severity="STATUS_CONFIG[status].severity"
  />
</template>
