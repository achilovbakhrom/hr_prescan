<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Skeleton from 'primevue/skeleton'
import GlassCard from '@/shared/components/GlassCard.vue'
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
</script>

<template>
  <GlassCard class="!p-0 overflow-hidden">
    <DataTable
      v-if="!loading"
      :value="vacancies"
      data-key="id"
      class="min-w-[860px] text-sm"
      striped-rows
      @row-click="emit('open', $event.data.id)"
    >
      <Column field="title" :header="t('vacancies.form.title')" class="max-w-[280px]">
        <template #body="{ data }">
          <div class="min-w-0">
            <p class="truncate font-medium text-[color:var(--color-text-primary)]">
              {{ data.title }}
            </p>
            <p
              v-if="data.companyName"
              class="truncate text-xs text-[color:var(--color-text-muted)]"
            >
              {{ data.companyName }}
            </p>
          </div>
        </template>
      </Column>
      <Column field="status" :header="t('common.status')" style="width: 130px">
        <template #body="{ data }">
          <VacancyStatusBadge :status="data.status" />
        </template>
      </Column>
      <Column field="candidatesTotal" :header="t('vacancies.applied')" style="width: 110px">
        <template #body="{ data }">
          <span class="font-mono font-semibold">{{ data.candidatesTotal ?? 0 }}</span>
        </template>
      </Column>
      <Column
        field="candidatesInterviewed"
        :header="t('vacancies.interviewed')"
        style="width: 120px"
      >
        <template #body="{ data }">
          <span class="font-mono">{{ data.candidatesInterviewed ?? 0 }}</span>
        </template>
      </Column>
      <Column
        field="candidatesShortlisted"
        :header="t('vacancies.shortlisted')"
        style="width: 120px"
      >
        <template #body="{ data }">
          <span class="font-mono">{{ data.candidatesShortlisted ?? 0 }}</span>
        </template>
      </Column>
      <Column field="createdAt" :header="t('common.createdAt')" style="width: 130px">
        <template #body="{ data }">
          <span class="text-[color:var(--color-text-secondary)]">
            {{ formatDate(data.createdAt) }}
          </span>
        </template>
      </Column>
      <Column :header="t('common.actions')" style="width: 220px">
        <template #body="{ data }">
          <div class="flex justify-end gap-2" @click.stop>
            <Button
              v-if="data.status === 'draft'"
              :label="t('vacancies.actions.publish')"
              icon="pi pi-send"
              size="small"
              @click="emit('statusChange', $event, data.id, 'published')"
            />
            <Button
              v-else-if="data.status === 'paused'"
              :label="t('vacancies.actions.resume')"
              icon="pi pi-play"
              severity="success"
              size="small"
              @click="emit('statusChange', $event, data.id, 'published')"
            />
            <Button
              v-else-if="data.status === 'published'"
              :label="t('vacancies.actions.pause')"
              icon="pi pi-pause"
              severity="warn"
              size="small"
              outlined
              @click="emit('statusChange', $event, data.id, 'paused')"
            />
            <Button
              v-if="data.status === 'draft' || data.status === 'archived'"
              icon="pi pi-trash"
              severity="danger"
              size="small"
              text
              :aria-label="t('common.delete')"
              @click="emit('delete', $event, data.id, data.title)"
            />
          </div>
        </template>
      </Column>
      <template #empty>
        <div class="py-10 text-center text-sm text-[color:var(--color-text-muted)]">
          {{ t('vacancies.noVacancies') }}
        </div>
      </template>
    </DataTable>
    <div v-else class="space-y-2 p-3" aria-busy="true">
      <Skeleton v-for="n in 6" :key="n" height="3rem" />
    </div>
  </GlassCard>
</template>
