<script setup lang="ts">
/**
 * VacancyListTable — DataTable rendering solid rows (legibility rule).
 * Glass chrome comes from PrimeVue overrides on pagination + the toolbar
 * that wraps the table. Mobile: horizontal scroll via the outer container.
 */
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import VacancyStatusBadge from './VacancyStatusBadge.vue'
import type { Vacancy, VacancyStatus } from '../types/vacancy.types'

defineProps<{
  vacancies: Vacancy[]
  loading: boolean
}>()

const emit = defineEmits<{
  open: [id: string]
  delete: [event: Event, id: string, title: string]
  statusChange: [event: Event, id: string, status: VacancyStatus]
}>()

const { t } = useI18n()

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString([], {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function onRowClick(event: { data: Vacancy }): void {
  emit('open', event.data.id)
}
</script>

<template>
  <div class="overflow-x-auto">
    <DataTable
      :value="vacancies"
      :loading="loading"
      striped-rows
      hoverable-rows
      paginator
      :rows="10"
      :rows-per-page-options="[10, 25, 50]"
      data-key="id"
      class="vacancy-table cursor-pointer"
      @row-click="onRowClick"
    >
      <Column field="title" :header="t('vacancies.title')" sortable>
        <template #body="{ data }">
          <div class="min-w-0">
            <p class="truncate font-medium text-[color:var(--color-text-primary)]">
              {{ (data as Vacancy).title }}
            </p>
            <p
              v-if="(data as Vacancy).companyName"
              class="truncate text-xs text-[color:var(--color-text-muted)]"
            >
              {{ (data as Vacancy).companyName }}
            </p>
          </div>
        </template>
      </Column>
      <Column :header="t('common.status')" sort-field="status" sortable>
        <template #body="{ data }">
          <VacancyStatusBadge :status="(data as Vacancy).status" />
        </template>
      </Column>
      <Column :header="t('vacancies.applied')" sort-field="candidatesTotal" sortable>
        <template #body="{ data }">
          <span class="font-mono text-sm text-[color:var(--color-text-primary)]">
            {{ (data as Vacancy).candidatesTotal ?? 0 }}
          </span>
        </template>
      </Column>
      <Column :header="t('common.createdAt')" sort-field="createdAt" sortable>
        <template #body="{ data }">
          <span class="text-xs text-[color:var(--color-text-muted)]">
            {{ formatDate((data as Vacancy).createdAt) }}
          </span>
        </template>
      </Column>
      <Column header="" :style="{ width: '14rem' }">
        <template #body="{ data }">
          <div class="flex items-center justify-end gap-1.5" @click.stop>
            <Button
              v-if="(data as Vacancy).status === 'draft'"
              :label="t('vacancies.actions.publish')"
              icon="pi pi-send"
              size="small"
              @click="emit('statusChange', $event, (data as Vacancy).id, 'published')"
            />
            <Button
              v-if="(data as Vacancy).status === 'paused'"
              :label="t('vacancies.actions.resume')"
              icon="pi pi-play"
              severity="success"
              size="small"
              @click="emit('statusChange', $event, (data as Vacancy).id, 'published')"
            />
            <Button
              v-if="(data as Vacancy).status === 'published'"
              :label="t('vacancies.actions.pause')"
              icon="pi pi-pause"
              severity="warn"
              size="small"
              outlined
              @click="emit('statusChange', $event, (data as Vacancy).id, 'paused')"
            />
            <Button
              v-if="(data as Vacancy).status === 'draft' || (data as Vacancy).status === 'archived'"
              icon="pi pi-trash"
              severity="danger"
              text
              rounded
              size="small"
              @click="emit('delete', $event, (data as Vacancy).id, (data as Vacancy).title)"
            />
          </div>
        </template>
      </Column>

      <template #empty>
        <div class="py-10 text-center text-[color:var(--color-text-muted)]">
          <i class="pi pi-briefcase mb-2 text-3xl"></i>
          <p class="text-sm">{{ t('vacancies.noVacancies') }}</p>
        </div>
      </template>
    </DataTable>
  </div>
</template>

<style scoped>
.vacancy-table :deep(.p-datatable-tbody > tr) {
  cursor: pointer;
}
</style>
