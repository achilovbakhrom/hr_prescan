<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import type { VacancyStatus } from '../types/vacancy.types'

const props = defineProps<{
  status: VacancyStatus
}>()

const { t } = useI18n()

const statusConfig = computed<
  Record<string, { label: string; severity: 'success' | 'info' | 'warn' | 'danger' | 'secondary' }>
>(() => ({
  draft: { label: t('vacancies.status.draft'), severity: 'secondary' },
  published: { label: t('vacancies.status.published'), severity: 'success' },
  paused: { label: t('vacancies.status.paused'), severity: 'warn' },
  archived: { label: t('vacancies.status.archived'), severity: 'secondary' },
  closed: { label: t('vacancies.status.closed'), severity: 'danger' },
}))

const config = computed(
  () => statusConfig.value[props.status] ?? { label: props.status, severity: 'secondary' as const },
)
</script>

<template>
  <Tag :value="config.label" :severity="config.severity" />
</template>
