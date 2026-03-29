<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import CandidateKanban from '@/features/candidates/components/CandidateKanban.vue'
import type { Application, ApplicationStatus } from '@/shared/types/candidate.types'
import { useCandidateActions } from '../composables/useCandidateActions'
import CandidatesToolbar from './CandidatesToolbar.vue'
import CandidatesTableView from './CandidatesTableView.vue'

const props = defineProps<{
  vacancyId: string
  interviewEnabled: boolean
}>()

const candidateStore = useCandidateStore()

const candidateViewMode = ref<'kanban' | 'table'>('kanban')
const statusFilter = ref<string | undefined>(undefined)
const orderingFilter = ref<string>('-created_at')
const searchQuery = ref('')
const selectedCandidates = ref<Application[]>([])
let searchTimeout: ReturnType<typeof setTimeout> | null = null

function fetchCandidates(): void {
  candidateStore.fetchVacancyCandidates(props.vacancyId, {
    status: statusFilter.value,
    ordering: orderingFilter.value,
    search: searchQuery.value || undefined,
  })
}

watch([statusFilter, orderingFilter], fetchCandidates)
onMounted(() => { fetchCandidates() })

function onSearchInput(): void {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(fetchCandidates, 300)
}

const actions = useCandidateActions(() => props.vacancyId, fetchCandidates)

function handleBulkAction(event: { value: ApplicationStatus }): void {
  actions.handleBulkAction(selectedCandidates.value, event.value, () => {
    selectedCandidates.value = []
  })
}
</script>

<template>
  <div class="space-y-3 py-3 sm:py-4">
    <CandidatesToolbar
      v-model:view-mode="candidateViewMode"
      v-model:status-filter="statusFilter"
      v-model:ordering-filter="orderingFilter"
      v-model:search-query="searchQuery"
      :selected-candidates="selectedCandidates"
      @search-input="onSearchInput"
      @bulk-action="handleBulkAction"
    />

    <p v-if="candidateStore.error" class="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-600">
      {{ candidateStore.error }}
    </p>

    <CandidateKanban
      v-if="candidateViewMode === 'kanban'"
      :candidates="candidateStore.candidates"
      :loading="candidateStore.loading"
      :interview-enabled="interviewEnabled"
      @status-change="actions.handleKanbanStatusChange"
      @batch-move="actions.handleBatchMove"
      @batch-move-by-score="actions.handleBatchMoveByScore"
      @batch-move-no-cv="actions.handleBatchMoveNoCv"
      @batch-move-by-days="actions.handleBatchMoveByDays"
      @soft-delete-all="actions.handleSoftDeleteAll"
    />

    <CandidatesTableView
      v-if="candidateViewMode === 'table'"
      v-model:selected-candidates="selectedCandidates"
      :interview-enabled="interviewEnabled"
      :confirm-row-status="actions.confirmRowStatus"
      :search-query="searchQuery"
    />
  </div>
</template>
