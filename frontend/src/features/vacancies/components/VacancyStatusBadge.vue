<script setup lang="ts">
import Tag from 'primevue/tag'
import type { VacancyStatus } from '../types/vacancy.types'

const props = defineProps<{
  status: VacancyStatus
}>()

const statusConfig: Record<
  string,
  { label: string; severity: 'success' | 'info' | 'warn' | 'danger' | 'secondary' }
> = {
  draft: { label: 'Draft', severity: 'secondary' },
  published: { label: 'Published', severity: 'success' },
  paused: { label: 'Paused', severity: 'warn' },
  archived: { label: 'Archived', severity: 'secondary' },
  closed: { label: 'Closed', severity: 'danger' },
}

const config = statusConfig[props.status] ?? { label: props.status, severity: 'secondary' as const }
</script>

<template>
  <Tag :value="config.label" :severity="config.severity" />
</template>
