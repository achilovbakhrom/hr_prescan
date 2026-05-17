<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import GlassCard from '@/shared/components/GlassCard.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import ApplicationStatusBadge from '../components/ApplicationStatusBadge.vue'
import { useCandidateBaseStore } from '../stores/candidateBase.store'
import type { HRCandidateRecord } from '../types/candidate.types'

const { t } = useI18n()
const router = useRouter()
const candidateStore = useCandidateBaseStore()
const search = ref('')
const ordering = ref('-last_activity_at')
let searchTimeout: ReturnType<typeof setTimeout> | null = null

const orderingOptions = computed(() => [
  { label: t('candidates.ordering.newest'), value: '-last_activity_at' },
  { label: t('candidates.ordering.oldest'), value: 'last_activity_at' },
  { label: t('candidates.ordering.nameAsc'), value: 'candidate_name' },
  { label: t('candidates.ordering.nameDesc'), value: '-candidate_name' },
])

function fetchCandidates(): void {
  void candidateStore.fetchCandidates({
    search: search.value || undefined,
    ordering: ordering.value,
  })
}

function onSearchInput(): void {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(fetchCandidates, 300)
}

function openCandidate(candidate: HRCandidateRecord): void {
  router.push({ name: ROUTE_NAMES.CANDIDATE_BASE_DETAIL, params: { id: candidate.id } })
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(value))
}

function scoreLabel(value: number | string | null): string {
  if (value === null || value === undefined || value === '') return '-'
  const numberValue = typeof value === 'string' ? Number(value) : value
  return Number.isNaN(numberValue) ? String(value) : numberValue.toFixed(1)
}

watch(ordering, fetchCandidates)
onMounted(fetchCandidates)
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-xl font-bold text-[color:var(--color-text-primary)] md:text-2xl">
          {{ t('nav.candidateBase') }}
        </h1>
        <p class="mt-0.5 text-sm text-[color:var(--color-text-muted)]">
          {{ candidateStore.candidates.length }} {{ t('nav.candidates').toLowerCase() }}
        </p>
      </div>
      <div class="flex flex-col gap-2 sm:flex-row">
        <InputText
          v-model="search"
          :placeholder="t('common.search')"
          class="w-full sm:w-72"
          @input="onSearchInput"
        />
        <Select
          v-model="ordering"
          :options="orderingOptions"
          option-label="label"
          option-value="value"
        />
      </div>
    </div>

    <p v-if="candidateStore.error" class="text-sm text-[color:var(--color-danger)]">
      {{ candidateStore.error }}
    </p>

    <GlassCard class="!p-0 overflow-hidden">
      <DataTable
        :value="candidateStore.candidates"
        :loading="candidateStore.loading"
        data-key="id"
        responsive-layout="scroll"
        striped-rows
        @row-click="openCandidate($event.data)"
      >
        <Column field="candidateName" :header="t('candidates.title')" style="min-width: 220px">
          <template #body="{ data }">
            <div class="min-w-0">
              <p class="truncate font-medium text-[color:var(--color-text-primary)]">
                {{ data.candidateName }}
              </p>
              <p class="truncate text-xs text-[color:var(--color-text-muted)]">
                {{ data.candidateEmail }}
              </p>
            </div>
          </template>
        </Column>
        <Column field="latestVacancyTitle" :header="t('nav.vacancies')" style="min-width: 220px" />
        <Column :header="t('common.status')" style="width: 130px">
          <template #body="{ data }">
            <ApplicationStatusBadge v-if="data.latestStatus" :status="data.latestStatus" />
          </template>
        </Column>
        <Column :header="t('candidates.overallScore')" style="width: 120px">
          <template #body="{ data }">{{ scoreLabel(data.latestMatchScore) }}</template>
        </Column>
        <Column :header="t('candidates.candidateBase.applications')" style="width: 110px">
          <template #body="{ data }">{{ data.applicationCount }}</template>
        </Column>
        <Column :header="t('common.updatedAt')" style="width: 150px">
          <template #body="{ data }">{{ formatDate(data.lastActivityAt) }}</template>
        </Column>
        <Column header="" style="width: 90px">
          <template #body="{ data }">
            <Button
              icon="pi pi-arrow-right"
              text
              rounded
              :aria-label="t('common.view')"
              @click.stop="openCandidate(data)"
            />
          </template>
        </Column>
      </DataTable>
    </GlassCard>
  </div>
</template>
