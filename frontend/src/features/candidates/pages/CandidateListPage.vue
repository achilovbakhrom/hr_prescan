<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'
import { useCandidateStore } from '../stores/candidate.store'
import ApplicationStatusBadge from '../components/ApplicationStatusBadge.vue'
import CandidateKanban from '../components/CandidateKanban.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Application, ApplicationStatus } from '../types/candidate.types'

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

const statusOptions = [
  { label: 'All Statuses', value: undefined },
  { label: 'Applied', value: 'applied' },
  { label: 'Interview In Progress', value: 'interview_in_progress' },
  { label: 'Interview Completed', value: 'interview_completed' },
  { label: 'Shortlisted', value: 'shortlisted' },
  { label: 'Rejected', value: 'rejected' },
  { label: 'Expired', value: 'expired' },
]

const orderingOptions = [
  { label: 'Newest first', value: '-created_at' },
  { label: 'Oldest first', value: 'created_at' },
  { label: 'Highest score', value: '-match_score' },
  { label: 'Lowest score', value: 'match_score' },
]

const bulkActionOptions = [
  { label: 'Shortlist', value: 'shortlisted' as ApplicationStatus },
  { label: 'Reject', value: 'rejected' as ApplicationStatus },
]

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
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button class="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600" @click="router.back()">
          <i class="pi pi-arrow-left"></i>
        </button>
        <div>
          <h1 class="text-xl font-bold text-gray-900">Candidate Pipeline</h1>
          <p class="text-sm text-gray-500">{{ candidateStore.candidates.length }} candidates</p>
        </div>
      </div>

      <!-- View toggle -->
      <div class="flex items-center gap-2 rounded-lg border border-gray-200 p-0.5">
        <button
          class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
          :class="viewMode === 'kanban' ? 'bg-gray-900 text-white' : 'text-gray-500 hover:text-gray-700'"
          @click="viewMode = 'kanban'"
        >
          <i class="pi pi-th-large mr-1.5"></i>Board
        </button>
        <button
          class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
          :class="viewMode === 'table' ? 'bg-gray-900 text-white' : 'text-gray-500 hover:text-gray-700'"
          @click="viewMode = 'table'"
        >
          <i class="pi pi-list mr-1.5"></i>Table
        </button>
      </div>
    </div>

    <p v-if="candidateStore.error" class="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-600">
      {{ candidateStore.error }}
    </p>

    <!-- Search (always visible) + Filters -->
    <div class="flex flex-wrap items-center gap-3">
      <div class="relative w-64">
        <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
        <InputText
          v-model="searchQuery"
          placeholder="Search by name or email..."
          class="w-full pl-9"
          @input="onSearchInput"
        />
      </div>

      <template v-if="viewMode === 'table'">
        <Dropdown
          v-model="statusFilter"
          :options="statusOptions"
          option-label="label"
          option-value="value"
          placeholder="Filter by status"
          class="w-48"
        />
        <Dropdown
          v-model="orderingFilter"
          :options="orderingOptions"
          option-label="label"
          option-value="value"
          placeholder="Sort by"
          class="w-48"
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
          class="w-40"
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
      <Column field="candidateName" header="Name" sortable />
      <Column field="candidateEmail" header="Email" sortable />
      <Column header="Status">
        <template #body="{ data }">
          <ApplicationStatusBadge :status="(data as Application).status" />
        </template>
      </Column>
      <Column header="Match Score" sortable sort-field="matchScore">
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
          <span v-else class="text-xs text-gray-400">Pending</span>
        </template>
      </Column>
      <Column header="Applied" sortable sort-field="createdAt">
        <template #body="{ data }">
          {{ formatDate((data as Application).createdAt) }}
        </template>
      </Column>
      <template #empty>
        <div class="py-8 text-center text-gray-500">
          <i class="pi pi-users mb-2 text-3xl"></i>
          <p v-if="searchQuery">No candidates matching "{{ searchQuery }}"</p>
          <p v-else>No candidates have applied yet</p>
        </div>
      </template>
    </DataTable>

    <ConfirmDialog />
  </div>
</template>
