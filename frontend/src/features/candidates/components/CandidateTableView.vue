<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import ApplicationStatusBadge from './ApplicationStatusBadge.vue'
import type { Application } from '../types/candidate.types'

defineProps<{
  candidates: Application[]
  loading: boolean
  selectedCandidates: Application[]
  searchQuery: string
  showVacancyColumn?: boolean
}>()

const emit = defineEmits<{
  'update:selectedCandidates': [value: Application[]]
  viewDetail: [candidate: Application]
}>()

const { t } = useI18n()

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}
</script>

<template>
  <DataTable
    :selection="selectedCandidates"
    :value="candidates"
    :loading="loading"
    striped-rows
    row-hover
    class="cursor-pointer"
    data-key="id"
    @update:selection="emit('update:selectedCandidates', $event)"
    @row-click="(e) => emit('viewDetail', e.data)"
  >
    <Column selection-mode="multiple" header-style="width: 3rem" />
    <Column field="candidateName" :header="t('candidates.application.name')" sortable />
    <Column field="candidateEmail" :header="t('candidates.application.email')" sortable />
    <Column v-if="showVacancyColumn" field="vacancyTitle" :header="t('nav.vacancies')" sortable>
      <template #body="{ data }">
        <span class="text-sm text-gray-700">{{ (data as Application).vacancyTitle }}</span>
      </template>
    </Column>
    <Column :header="t('common.status')">
      <template #body="{ data }"
        ><ApplicationStatusBadge :status="(data as Application).status"
      /></template>
    </Column>
    <Column :header="t('candidates.matchScore')" sortable sort-field="matchScore">
      <template #body="{ data }">
        <span
          v-if="(data as Application).matchScore !== null"
          class="rounded-md px-2 py-0.5 text-xs font-medium"
          :class="
            (data as Application).matchScore! >= 70
              ? 'bg-emerald-50 text-emerald-700'
              : (data as Application).matchScore! >= 40
                ? 'bg-amber-50 text-amber-700'
                : 'bg-red-50 text-red-700'
          "
          >{{ (data as Application).matchScore }}%</span
        >
        <span v-else class="text-xs text-gray-400">{{ t('interviews.status.pending') }}</span>
      </template>
    </Column>
    <Column :header="t('common.createdAt')" sortable sort-field="createdAt">
      <template #body="{ data }">{{ formatDate((data as Application).createdAt) }}</template>
    </Column>
    <template #empty>
      <div class="py-8 text-center text-gray-500">
        <i class="pi pi-users mb-2 text-3xl"></i>
        <p v-if="searchQuery">{{ t('candidates.noMatchingCandidates', { query: searchQuery }) }}</p>
        <p v-else>{{ t('candidates.noCandidates') }}</p>
      </div>
    </template>
  </DataTable>
</template>
