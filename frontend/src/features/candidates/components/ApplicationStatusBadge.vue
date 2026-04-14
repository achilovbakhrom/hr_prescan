<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import type { ApplicationStatus } from '../types/candidate.types'

const props = defineProps<{
  status: ApplicationStatus
}>()

const { t } = useI18n()

const STATUS_CONFIG = computed<Record<ApplicationStatus, { label: string; severity: string }>>(
  () => ({
    applied: { label: t('candidates.status.applied'), severity: 'info' },
    prescanned: { label: t('candidates.status.prescanned'), severity: 'info' },
    interviewed: { label: t('candidates.status.interviewed'), severity: 'success' },
    shortlisted: { label: t('candidates.status.shortlisted'), severity: 'success' },
    hired: { label: t('candidates.status.hired'), severity: 'success' },
    rejected: { label: t('candidates.status.rejected'), severity: 'danger' },
    expired: { label: t('candidates.status.expired'), severity: 'secondary' },
    archived: { label: t('candidates.status.archived'), severity: 'secondary' },
  }),
)
</script>

<template>
  <Tag
    :value="STATUS_CONFIG[props.status].label"
    :severity="STATUS_CONFIG[props.status].severity"
  />
</template>
