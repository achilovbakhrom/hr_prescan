<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'
import { useCandidateStore } from '../stores/candidate.store'
import CandidateKanban from '../components/CandidateKanban.vue'
import CandidateTableView from '../components/CandidateTableView.vue'
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

const bulkActionOptions = computed(() => [
  { label: t('candidates.actions.shortlist'), value: 'shortlisted' as ApplicationStatus },
  { label: t('candidates.actions.reject'), value: 'rejected' as ApplicationStatus },
])

function fetchCandidates(): void {
  const params = {
    status: statusFilter.value,
    ordering: orderingFilter.value,
    search: searchQuery.value || undefined,
  }
  if (isAllCandidates.value) {
    candidateStore.fetchAllCandidates(params)
  } else {
    candidateStore.fetchVacancyCandidates(vacancyId.value, params)
  }
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

function handleBulkAction(event: { value: ApplicationStatus }): void {
  const status = event.value
  const count = selectedCandidates.value.length
  confirm.require({
    message: t('candidates.dialogs.bulkConfirmMessage', {
      action: status === 'shortlisted' ? 'shortlist' : 'reject',
      count,
    }),
    header: t('candidates.dialogs.bulkConfirmHeader'),
    icon: 'pi pi-exclamation-triangle',
    acceptClass: status === 'rejected' ? 'p-button-danger' : 'p-button-success',
    accept: async () => {
      await candidateStore
        .bulkUpdateStatus(
          selectedCandidates.value.map((c) => c.id),
          status,
        )
        .catch(() => {})
      selectedCandidates.value = []
    },
  })
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
          status: status.replace(/_/g, ' '),
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
          class="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
          @click="router.back()"
        >
          <i class="pi pi-arrow-left"></i>
        </button>
        <div>
          <h1 class="text-lg font-bold text-gray-900 md:text-xl">
            {{ isAllCandidates ? t('nav.allCandidates') : t('candidates.pipeline') }}
          </h1>
          <p class="text-sm text-gray-500">
            {{ candidateStore.candidates.length }} {{ t('nav.candidates').toLowerCase() }}
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2 rounded-lg border border-gray-200 p-0.5">
        <button
          class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
          :class="
            viewMode === 'kanban' ? 'bg-gray-900 text-white' : 'text-gray-500 hover:text-gray-700'
          "
          @click="viewMode = 'kanban'"
        >
          <i class="pi pi-th-large mr-1.5"></i>{{ t('candidates.kanban') }}
        </button>
        <button
          class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
          :class="
            viewMode === 'table' ? 'bg-gray-900 text-white' : 'text-gray-500 hover:text-gray-700'
          "
          @click="viewMode = 'table'"
        >
          <i class="pi pi-list mr-1.5"></i>{{ t('candidates.table') }}
        </button>
      </div>
    </div>

    <p v-if="candidateStore.error" class="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-600">
      {{ candidateStore.error }}
    </p>

    <div class="flex flex-wrap items-center gap-3">
      <IconField class="w-full sm:w-64"
        ><InputIcon class="pi pi-search" /><InputText
          v-model="searchQuery"
          :placeholder="t('candidates.search')"
          class="w-full"
          @input="onSearchInput"
      /></IconField>
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

    <CandidateKanban
      v-if="viewMode === 'kanban'"
      :candidates="candidateStore.candidates"
      :loading="candidateStore.loading"
      @status-change="handleKanbanStatusChange"
    />
    <CandidateTableView
      v-if="viewMode === 'table'"
      :candidates="candidateStore.candidates"
      :loading="candidateStore.loading"
      v-model:selected-candidates="selectedCandidates"
      :search-query="searchQuery"
      :show-vacancy-column="isAllCandidates"
      @view-detail="viewDetail"
    />

    <ConfirmDialog />
  </div>
</template>
