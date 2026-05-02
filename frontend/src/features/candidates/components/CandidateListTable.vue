<script setup lang="ts">
/**
 * CandidateListTable — HR-facing candidate list DataTable.
 * Avatar + name + vacancy + score chip + status badge.
 * Solid rows (data legibility rule); glass comes from the outer GlassCard.
 */
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

function initials(name: string | undefined): string {
  if (!name) return '?'
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0]!.toUpperCase())
    .join('')
}

function scoreClasses(score: number): string {
  if (score >= 70) return 'bg-[color:var(--color-success)]/15 text-[color:var(--color-success)]'
  if (score >= 40) return 'bg-[color:var(--color-warning)]/15 text-[color:var(--color-warning)]'
  return 'bg-[color:var(--color-danger)]/15 text-[color:var(--color-danger)]'
}
</script>

<template>
  <div class="overflow-x-auto">
    <DataTable
      :selection="selectedCandidates"
      :value="candidates"
      :loading="loading"
      striped-rows
      row-hover
      paginator
      :rows="10"
      :rows-per-page-options="[10, 25, 50]"
      class="cursor-pointer"
      data-key="id"
      @update:selection="emit('update:selectedCandidates', $event)"
      @row-click="(e) => emit('viewDetail', e.data)"
    >
      <Column selection-mode="multiple" header-style="width: 3rem" />
      <Column :header="t('candidates.application.name')" sortable sort-field="candidateName">
        <template #body="{ data }">
          <div class="flex items-center gap-2">
            <div
              class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[color:var(--color-accent-soft)] text-xs font-semibold text-[color:var(--color-accent)]"
            >
              {{ initials((data as Application).candidateName) }}
            </div>
            <div class="min-w-0">
              <p class="truncate font-medium text-[color:var(--color-text-primary)]">
                {{ (data as Application).candidateName }}
              </p>
              <p class="truncate text-xs text-[color:var(--color-text-muted)]">
                {{ (data as Application).candidateEmail }}
              </p>
            </div>
          </div>
        </template>
      </Column>
      <Column v-if="showVacancyColumn" field="vacancyTitle" :header="t('nav.vacancies')" sortable>
        <template #body="{ data }">
          <span class="truncate text-sm text-[color:var(--color-text-secondary)]">
            {{ (data as Application).vacancyTitle }}
          </span>
        </template>
      </Column>
      <Column :header="t('common.status')">
        <template #body="{ data }">
          <ApplicationStatusBadge :status="(data as Application).status" />
        </template>
      </Column>
      <Column :header="t('candidates.matchScore')" sortable sort-field="matchScore">
        <template #body="{ data }">
          <span
            v-if="(data as Application).matchScore !== null"
            class="rounded-md px-2 py-0.5 font-mono text-xs font-semibold"
            :class="scoreClasses((data as Application).matchScore as number)"
            >{{ (data as Application).matchScore }}%</span
          >
          <span v-else class="text-xs text-[color:var(--color-text-muted)]">{{
            t('interviews.status.pending')
          }}</span>
        </template>
      </Column>
      <Column :header="t('common.createdAt')" sortable sort-field="createdAt">
        <template #body="{ data }">
          <span class="text-xs text-[color:var(--color-text-muted)]">
            {{ formatDate((data as Application).createdAt) }}
          </span>
        </template>
      </Column>
      <template #empty>
        <div class="py-10 text-center text-[color:var(--color-text-muted)]">
          <i class="pi pi-users mb-2 text-3xl"></i>
          <p v-if="searchQuery" class="text-sm">
            {{ t('candidates.noMatchingCandidates', { query: searchQuery }) }}
          </p>
          <p v-else class="text-sm">{{ t('candidates.noCandidates') }}</p>
        </div>
      </template>
    </DataTable>
  </div>
</template>
