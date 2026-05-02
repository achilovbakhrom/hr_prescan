<script setup lang="ts">
/**
 * CandidateListPage — HR-facing list, redesigned with glass primitives.
 * Preserves tenant scoping (store already filters by active company via
 * CompanySwitcher) and the kanban/table toggle.
 * Spec: docs/design/spec.md §9 Candidates.
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'
import GlassCard from '@/shared/components/GlassCard.vue'
import { useCandidateStore } from '../stores/candidate.store'
import CandidateKanban from '../components/CandidateKanban.vue'
import CandidateListTable from '../components/CandidateListTable.vue'
import CandidateListToolbar from '../components/CandidateListToolbar.vue'
import { useKanbanBatchActions } from '../composables/useKanbanBatchActions'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Application, ApplicationStatus } from '../types/candidate.types'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const confirm = useConfirm()
const candidateStore = useCandidateStore()
const vacancyId = computed(() => (route.params.vacancyId as string) || '')
const isAllCandidates = computed(() => !vacancyId.value)

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

function fetchCandidates(): void {
  const params = {
    status: statusFilter.value,
    ordering: orderingFilter.value,
    search: searchQuery.value || undefined,
  }
  if (isAllCandidates.value) candidateStore.fetchAllCandidates(params)
  else candidateStore.fetchVacancyCandidates(vacancyId.value, params)
}

onMounted(fetchCandidates)
watch([statusFilter, orderingFilter], fetchCandidates)

function onSearchInput(): void {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(fetchCandidates, 300)
}

const batchActions = useKanbanBatchActions(
  () => candidateStore.candidates,
  () => vacancyId.value,
  fetchCandidates,
)

function viewDetail(candidate: Application): void {
  router.push({ name: ROUTE_NAMES.CANDIDATE_DETAIL, params: { id: candidate.id } })
}

function handleKanbanStatusChange(candidateId: string, status: ApplicationStatus): void {
  const candidate = candidateStore.candidates.find((c) => c.id === candidateId)
  if (!candidate) return
  const isReset = status === 'applied'
  confirm.require({
    message: isReset
      ? t('candidates.dialogs.resetMessage', { name: candidate.candidateName })
      : t('candidates.dialogs.moveMessage', {
          name: candidate.candidateName,
          status: t(`candidates.status.${status}`),
        }),
    header: isReset
      ? t('candidates.dialogs.resetHeader')
      : t('candidates.dialogs.statusChangeHeader'),
    icon: isReset ? 'pi pi-refresh' : 'pi pi-exclamation-triangle',
    acceptLabel: isReset ? t('candidates.dialogs.yesReset') : t('candidates.dialogs.yesMove'),
    rejectLabel: t('common.cancel'),
    accept: async () => {
      await candidateStore.updateStatus(candidateId, status).catch(() => {})
    },
  })
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex items-center gap-3">
        <button
          v-if="!isAllCandidates"
          class="rounded-lg p-1.5 text-[color:var(--color-text-muted)] transition-colors hover:bg-[color:var(--color-surface-sunken)] hover:text-[color:var(--color-text-primary)]"
          @click="router.back()"
        >
          <i class="pi pi-arrow-left"></i>
        </button>
        <div>
          <h1 class="text-xl font-bold text-[color:var(--color-text-primary)] md:text-2xl">
            {{ isAllCandidates ? t('nav.allCandidates') : t('candidates.pipeline') }}
          </h1>
          <p class="mt-0.5 text-sm text-[color:var(--color-text-muted)]">
            {{ candidateStore.candidates.length }} {{ t('nav.candidates').toLowerCase() }}
          </p>
        </div>
      </div>
      <div
        class="inline-flex rounded-md bg-[color:var(--color-surface-sunken)] p-0.5"
        role="tablist"
      >
        <button
          class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
          :class="
            viewMode === 'kanban'
              ? 'bg-[color:var(--color-surface-raised)] text-[color:var(--color-text-primary)] shadow-sm'
              : 'text-[color:var(--color-text-muted)] hover:text-[color:var(--color-text-primary)]'
          "
          @click="viewMode = 'kanban'"
        >
          <i class="pi pi-th-large mr-1.5"></i>{{ t('candidates.kanban') }}
        </button>
        <button
          class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
          :class="
            viewMode === 'table'
              ? 'bg-[color:var(--color-surface-raised)] text-[color:var(--color-text-primary)] shadow-sm'
              : 'text-[color:var(--color-text-muted)] hover:text-[color:var(--color-text-primary)]'
          "
          @click="viewMode = 'table'"
        >
          <i class="pi pi-list mr-1.5"></i>{{ t('candidates.table') }}
        </button>
      </div>
    </div>

    <p
      v-if="candidateStore.error"
      class="rounded-lg border border-[color:var(--color-danger)] bg-[color:var(--color-danger)]/10 px-4 py-2 text-sm text-[color:var(--color-danger)]"
    >
      {{ candidateStore.error }}
    </p>

    <CandidateListToolbar
      v-model:search="searchQuery"
      v-model:status-filter="statusFilter"
      v-model:ordering-filter="orderingFilter"
      :status-options="statusOptions"
      :ordering-options="orderingOptions"
      :show-filters="viewMode === 'table'"
      @search-input="onSearchInput"
    />

    <GlassCard v-if="viewMode === 'table'" class="!p-0 overflow-hidden">
      <CandidateListTable
        v-model:selected-candidates="selectedCandidates"
        :candidates="candidateStore.candidates"
        :loading="candidateStore.loading"
        :search-query="searchQuery"
        :show-vacancy-column="isAllCandidates"
        @view-detail="viewDetail"
      />
    </GlassCard>

    <CandidateKanban
      v-else
      :candidates="candidateStore.candidates"
      :loading="candidateStore.loading"
      :interview-enabled="true"
      @status-change="handleKanbanStatusChange"
      @batch-move="batchActions.handleBatchMove"
      @batch-move-by-score="batchActions.handleBatchMoveByScore"
      @batch-move-no-cv="batchActions.handleBatchMoveNoCv"
      @batch-move-by-days="batchActions.handleBatchMoveByDays"
      @soft-delete-all="batchActions.handleSoftDeleteAll"
    />

    <ConfirmDialog />
  </div>
</template>
