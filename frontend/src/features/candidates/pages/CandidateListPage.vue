<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'
import { useCandidateStore } from '../stores/candidate.store'
import ApplicationStatusBadge from '../components/ApplicationStatusBadge.vue'
import CandidateKanban from '../components/CandidateKanban.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Application, ApplicationStatus } from '../types/candidate.types'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()
const confirm = useConfirm()
const candidateStore = useCandidateStore()
const vacancyId = computed(() => route.params.vacancyId as string)

const viewMode = ref<'kanban' | 'table'>('kanban')
const statusFilter = ref<string | undefined>(undefined)
const orderingFilter = ref<string>('-created_at')
const searchQuery = ref('')
const selectedCandidates = ref<Application[]>([])

let searchTimeout: ReturnType<typeof setTimeout> | null = null

const statusOptions = computed(() => [
  { label: t('vacancies.allStatuses'), value: undefined },
  { label: t('candidates.status.applied'), value: 'applied' },
  { label: t('candidates.status.prescanned'), value: 'prescanned' },
  { label: t('candidates.status.interviewed'), value: 'interviewed' },
  { label: t('candidates.status.shortlisted'), value: 'shortlisted' },
  { label: t('candidates.status.rejected'), value: 'rejected' },
  { label: t('candidates.status.expired'), value: 'expired' },
])

const orderingOptions = computed(() => [
  { label: t('candidates.ordering.newest'), value: '-created_at' },
  { label: t('candidates.ordering.oldest'), value: 'created_at' },
  { label: t('candidates.ordering.highestScore'), value: '-match_score' },
  { label: t('candidates.ordering.lowestScore'), value: 'match_score' },
])

const bulkActionOptions = computed(() => [
  { label: t('candidates.actions.shortlist'), value: 'shortlisted' as ApplicationStatus },
  { label: t('candidates.actions.reject'), value: 'rejected' as ApplicationStatus },
])

function fetchCandidates(): void {
  candidateStore.fetchVacancyCandidates(vacancyId.value, {
    status: statusFilter.value,
    ordering: orderingFilter.value,
    search: searchQuery.value || undefined,
  })
}

onMounted(fetchCandidates)
watch([statusFilter, orderingFilter], fetchCandidates)

function onSearchInput(): void {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(fetchCandidates, 300)
}

function viewDetail(candidate: Application): void {
  router.push({ name: ROUTE_NAMES.CANDIDATE_DETAIL, params: { id: candidate.id } })
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}

function handleBulkAction(event: { value: ApplicationStatus }): void {
  const status = event.value
  const count = selectedCandidates.value.length
  const label = status === 'shortlisted' ? 'shortlist' : 'reject'

  confirm.require({
    message: `Are you sure you want to ${label} ${count} candidate(s)?`,
    header: 'Confirm Bulk Action',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: status === 'rejected' ? 'p-button-danger' : 'p-button-success',
    accept: async () => {
      const ids = selectedCandidates.value.map((c) => c.id)
      await candidateStore.bulkUpdateStatus(ids, status).catch(() => {})
      selectedCandidates.value = []
    },
  })
}

function handleKanbanStatusChange(candidateId: string, status: ApplicationStatus): void {
  const candidate = candidateStore.candidates.find((c) => c.id === candidateId)
  if (!candidate) return

  const statusLabel = status.replace(/_/g, ' ')
  const isReset = status === 'applied'
  const message = isReset
    ? `Reset ${candidate.candidateName} back to "Applied"? This will clear their current status.`
    : `Move ${candidate.candidateName} to "${statusLabel}"?`

  confirm.require({
    message,
    header: isReset ? 'Reset Candidate Status' : 'Confirm Status Change',
    icon: isReset ? 'pi pi-refresh' : 'pi pi-exclamation-triangle',
    acceptLabel: isReset ? 'Yes, reset' : 'Yes, move',
    rejectLabel: 'Cancel',
    accept: async () => {
      await candidateStore.updateStatus(candidateId, status).catch(() => {})
    },
  })
}
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex items-center gap-3">
        <button class="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600" @click="router.back()">
          <i class="pi pi-arrow-left"></i>
        </button>
        <div>
          <h1 class="text-lg font-bold text-gray-900 md:text-xl">{{ t('candidates.pipeline') }}</h1>
          <p class="text-sm text-gray-500">{{ candidateStore.candidates.length }} {{ t('nav.candidates').toLowerCase() }}</p>
        </div>
      </div>

      <!-- View toggle -->
      <div class="flex items-center gap-2 rounded-lg border border-gray-200 p-0.5">
        <button
          class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
          :class="viewMode === 'kanban' ? 'bg-gray-900 text-white' : 'text-gray-500 hover:text-gray-700'"
          @click="viewMode = 'kanban'"
        >
          <i class="pi pi-th-large mr-1.5"></i>{{ t('candidates.kanban') }}
        </button>
        <button
          class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
          :class="viewMode === 'table' ? 'bg-gray-900 text-white' : 'text-gray-500 hover:text-gray-700'"
          @click="viewMode = 'table'"
        >
          <i class="pi pi-list mr-1.5"></i>{{ t('candidates.table') }}
        </button>
      </div>
    </div>

    <p v-if="candidateStore.error" class="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-600">
      {{ candidateStore.error }}
    </p>

    <!-- Search (always visible) + Filters -->
    <div class="flex flex-wrap items-center gap-3">
      <IconField class="w-full sm:w-64">
        <InputIcon class="pi pi-search" />
        <InputText
          v-model="searchQuery"
          :placeholder="t('candidates.search')"
          class="w-full"
          @input="onSearchInput"
        />
      </IconField>

      <template v-if="viewMode === 'table'">
        <Dropdown
          v-model="statusFilter"
          :options="statusOptions"
          option-label="label"
          option-value="value"
          placeholder="Filter by status"
          class="w-full sm:w-48"
        />
        <Dropdown
          v-model="orderingFilter"
          :options="orderingOptions"
          option-label="label"
          option-value="value"
          placeholder="Sort by"
          class="w-full sm:w-48"
        />
      </template>

      <div v-if="selectedCandidates.length > 0" class="flex items-center gap-2">
        <span class="text-sm text-gray-600">{{ selectedCandidates.length }} selected</span>
        <Dropdown
          :model-value="null"
          :options="bulkActionOptions"
          option-label="label"
          option-value="value"
          placeholder="Bulk Actions"
          class="w-full sm:w-40"
          @change="handleBulkAction"
        />
      </div>
    </div>

    <!-- Kanban View -->
    <CandidateKanban
      v-if="viewMode === 'kanban'"
      :candidates="candidateStore.candidates"
      :loading="candidateStore.loading"
      @status-change="handleKanbanStatusChange"
    />

    <!-- Table View -->
    <DataTable
      v-if="viewMode === 'table'"
      v-model:selection="selectedCandidates"
      :value="candidateStore.candidates"
      :loading="candidateStore.loading"
      striped-rows
      row-hover
      class="cursor-pointer"
      data-key="id"
      @row-click="(e) => viewDetail(e.data)"
    >
      <Column selection-mode="multiple" header-style="width: 3rem" />
      <Column field="candidateName" :header="t('candidates.application.name')" sortable />
      <Column field="candidateEmail" :header="t('candidates.application.email')" sortable />
      <Column :header="t('common.status')">
        <template #body="{ data }">
          <ApplicationStatusBadge :status="(data as Application).status" />
        </template>
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
          >
            {{ (data as Application).matchScore }}%
          </span>
          <span v-else class="text-xs text-gray-400">{{ t('interviews.status.pending') }}</span>
        </template>
      </Column>
      <Column :header="t('common.createdAt')" sortable sort-field="createdAt">
        <template #body="{ data }">
          {{ formatDate((data as Application).createdAt) }}
        </template>
      </Column>
      <template #empty>
        <div class="py-8 text-center text-gray-500">
          <i class="pi pi-users mb-2 text-3xl"></i>
          <p v-if="searchQuery">No candidates matching "{{ searchQuery }}"</p>
          <p v-else>{{ t('candidates.noCandidates') }}</p>
        </div>
      </template>
    </DataTable>

    <ConfirmDialog />
  </div>
</template>
