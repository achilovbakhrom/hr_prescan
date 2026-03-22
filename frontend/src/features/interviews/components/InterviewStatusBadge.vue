<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import type { InterviewStatus } from '../types/interview.types'

const props = defineProps<{
  status: InterviewStatus
}>()

const { t } = useI18n()

const statusConfig = computed<Record<
  InterviewStatus,
  { label: string; severity: 'success' | 'info' | 'warn' | 'danger' | 'secondary' }
>>(() => ({
  pending: { label: t('interviews.status.pending'), severity: 'warn' },
  in_progress: { label: t('interviews.status.inProgress'), severity: 'info' },
  completed: { label: t('interviews.status.completed'), severity: 'success' },
  cancelled: { label: t('interviews.status.cancelled'), severity: 'danger' },
  expired: { label: t('interviews.status.expired'), severity: 'secondary' },
}))

const config = computed(() => statusConfig.value[props.status] ?? { label: props.status, severity: 'secondary' as const })
</script>

<template>
  <Tag :value="config.label" :severity="config.severity" />
</template>
