<script setup lang="ts">
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
import CandidateViewModeToggle from '../components/CandidateViewModeToggle.vue'
import { useKanbanBatchActions } from '../composables/useKanbanBatchActions'
import { useVacancyStore } from '@/features/vacancies/stores/vacancy.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Application, ApplicationStatus } from '../types/candidate.types'
import type { Vacancy } from '@/features/vacancies/types/vacancy.types'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const confirm = useConfirm()
const candidateStore = useCandidateStore()
const vacancyStore = useVacancyStore()
const vacancyId = computed(() => (route.params.vacancyId as string) || '')
const isAllCandidates = computed(() => !vacancyId.value)

const viewMode = ref<'kanban' | 'table'>('kanban')
const statusFilter = ref<string | undefined>(undefined)
const orderingFilter = ref<string>('-created_at')
const searchQuery = ref('')
const selectedVacancy = ref<Vacancy | null>(null)
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
const vacancyOptions = computed(() => vacancyStore.vacancies.filter((v) => v.status !== 'archived'))

function fetchCandidates(): void {
  const params = {
    status: statusFilter.value,
    ordering: orderingFilter.value,
    search: searchQuery.value || undefined,
    vacancyId: isAllCandidates.value ? selectedVacancy.value?.id : undefined,
  }
  if (isAllCandidates.value) candidateStore.fetchAllCandidates(params)
  else candidateStore.fetchVacancyCandidates(vacancyId.value, params)
}

onMounted(() => {
  fetchCandidates()
  if (isAllCandidates.value) vacancyStore.fetchVacancies()
})
watch([statusFilter, orderingFilter, selectedVacancy], fetchCandidates)

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
      <CandidateViewModeToggle v-model="viewMode" />
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
      :show-vacancy-filter="isAllCandidates"
      :vacancy-filter="selectedVacancy"
      :vacancy-options="vacancyOptions"
      @search-input="onSearchInput"
      @update:vacancy-filter="selectedVacancy = $event"
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
