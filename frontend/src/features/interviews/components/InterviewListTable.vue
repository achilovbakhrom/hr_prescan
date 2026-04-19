<script setup lang="ts">
/**
 * InterviewListTable — HR interview list DataTable (solid rows).
 */
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import InterviewStatusBadge from './InterviewStatusBadge.vue'
import type { Interview } from '../types/interview.types'

defineProps<{
  interviews: Interview[]
  loading: boolean
}>()

const emit = defineEmits<{
  open: [id: string]
}>()

const { t } = useI18n()

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}

function formatScore(score: number | null): string {
  return score !== null ? `${score}/10` : '—'
}

function formatSessionType(type: string): string {
  return type === 'prescanning' ? t('candidates.prescanning') : t('candidates.interview')
}

function sessionTypeSeverity(type: string): 'success' | 'info' {
  return type === 'prescanning' ? 'info' : 'success'
}

function onRowClick(event: { data: Interview }): void {
  emit('open', event.data.id)
}
</script>

<template>
  <div class="overflow-x-auto">
    <DataTable
      :value="interviews"
      :loading="loading"
      striped-rows
      row-hover
      paginator
      :rows="10"
      :rows-per-page-options="[10, 25, 50]"
      class="cursor-pointer"
      data-key="id"
      @row-click="onRowClick"
    >
      <Column field="candidateName" :header="t('nav.candidates')" sortable>
        <template #body="{ data }">
          <p class="font-medium text-[color:var(--color-text-primary)]">
            {{ (data as Interview).candidateName }}
          </p>
        </template>
      </Column>
      <Column field="vacancyTitle" :header="t('nav.vacancies')" sortable>
        <template #body="{ data }">
          <span class="text-sm text-[color:var(--color-text-secondary)]">
            {{ (data as Interview).vacancyTitle }}
          </span>
        </template>
      </Column>
      <Column :header="t('interviews.title')" sort-field="sessionType">
        <template #body="{ data }">
          <Tag
            :value="formatSessionType((data as Interview).sessionType)"
            :severity="sessionTypeSeverity((data as Interview).sessionType)"
          />
        </template>
      </Column>
      <Column :header="t('common.createdAt')" sortable sort-field="createdAt">
        <template #body="{ data }">
          <span class="text-xs text-[color:var(--color-text-muted)]">
            {{ formatDate((data as Interview).createdAt) }}
          </span>
        </template>
      </Column>
      <Column :header="t('common.status')" sort-field="status">
        <template #body="{ data }">
          <InterviewStatusBadge :status="(data as Interview).status" />
        </template>
      </Column>
      <Column :header="t('interviews.overallScore')">
        <template #body="{ data }">
          <span class="font-mono text-sm text-[color:var(--color-text-primary)]">
            {{ formatScore((data as Interview).overallScore) }}
          </span>
        </template>
      </Column>

      <template #empty>
        <div class="py-10 text-center text-[color:var(--color-text-muted)]">
          <i class="pi pi-comments mb-2 text-3xl"></i>
          <p class="text-sm">{{ t('common.noResults') }}</p>
        </div>
      </template>
    </DataTable>
  </div>
</template>
