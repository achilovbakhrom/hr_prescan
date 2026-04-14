<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Menu from 'primevue/menu'
import { useConfirm } from 'primevue/useconfirm'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import { candidateService } from '@/features/candidates/services/candidate.service'
import CandidateKanban from '@/features/candidates/components/CandidateKanban.vue'
import ApplicationStatusBadge from '@/features/candidates/components/ApplicationStatusBadge.vue'
import type { Application, ApplicationStatus } from '@/shared/types/candidate.types'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const props = defineProps<{
  vacancyId: string
  interviewEnabled: boolean
}>()

const { t } = useI18n()
const router = useRouter()
const confirm = useConfirm()
const candidateStore = useCandidateStore()

// --- Candidates tab state ---
const candidateViewMode = ref<'kanban' | 'table'>('kanban')
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
  { label: t('candidates.status.hired'), value: 'hired' },
  { label: t('candidates.status.rejected'), value: 'rejected' },
  { label: t('candidates.status.expired'), value: 'expired' },
  { label: t('candidates.status.archived'), value: 'archived' },
])

const orderingOptions = computed(() => [
  { label: t('candidates.ordering.newest'), value: '-created_at' },
  { label: t('candidates.ordering.oldest'), value: 'created_at' },
  { label: t('candidates.ordering.highestScore'), value: '-match_score' },
  { label: t('candidates.ordering.lowestScore'), value: 'match_score' },
])

const bulkActionOptions = computed(() => [
  { label: t('candidates.actions.shortlist'), value: 'shortlisted' as ApplicationStatus },
  { label: t('candidates.actions.hire'), value: 'hired' as ApplicationStatus },
  { label: t('candidates.actions.reject'), value: 'rejected' as ApplicationStatus },
  { label: t('candidates.actions.archive'), value: 'archived' as ApplicationStatus },
  { label: t('candidates.actions.reset'), value: 'applied' as ApplicationStatus },
])

// --- Data fetching ---

function fetchCandidates(): void {
  candidateStore.fetchVacancyCandidates(props.vacancyId, {
    status: statusFilter.value,
    ordering: orderingFilter.value,
    search: searchQuery.value || undefined,
  })
}

watch([statusFilter, orderingFilter], fetchCandidates)

function onSearchInput(): void {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(fetchCandidates, 300)
}

onMounted(() => {
  fetchCandidates()
})

// --- Navigation ---

function viewCandidateDetail(candidate: Application): void {
  router.push({ name: ROUTE_NAMES.CANDIDATE_DETAIL, params: { id: candidate.id } })
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}

// --- Table score helpers ---

function getTableOverallScore(c: Application): number | null {
  const cv = c.matchScore != null ? Number(c.matchScore) : null
  const ps = c.prescanningScore != null ? Number(c.prescanningScore) * 10 : null
  const iv = c.interviewScore != null ? Number(c.interviewScore) * 10 : null
  if (cv != null && ps != null && iv != null) return Math.round(cv * 0.2 + ps * 0.3 + iv * 0.5)
  if (cv != null && ps != null) return Math.round(cv * 0.4 + ps * 0.6)
  if (ps != null && iv != null) return Math.round(ps * 0.4 + iv * 0.6)
  if (cv != null) return Math.round(cv)
  if (ps != null) return Math.round(ps)
  if (iv != null) return Math.round(iv)
  return null
}

function getTableScoreClasses(score: number): string {
  if (score >= 70) return 'border-emerald-400 text-emerald-600'
  if (score >= 45) return 'border-amber-400 text-amber-600'
  return 'border-red-400 text-red-500'
}

function getTableScoreBadge(score: number, max: number): string {
  const pct = (score / max) * 100
  if (pct >= 70) return 'bg-emerald-50 text-emerald-700'
  if (pct >= 45) return 'bg-amber-50 text-amber-700'
  return 'bg-red-50 text-red-700'
}

// --- Table row menu ---

const rowMenuRefs = ref<Record<string, InstanceType<typeof Menu> | null>>({})

function setRowMenuRef(id: string, el: unknown) {
  rowMenuRefs.value[id] = el as InstanceType<typeof Menu> | null
}

function toggleRowMenu(event: Event, id: string) {
  rowMenuRefs.value[id]?.toggle(event)
}

function getRowMenuItems(c: Application) {
  const s = c.status
  const items: { label: string; icon: string; command: () => void; separator?: boolean }[] = []

  items.push({
    label: 'View details',
    icon: 'pi pi-eye',
    command: () => viewCandidateDetail(c),
  })
  items.push({ label: '', icon: '', command: () => {}, separator: true })

  // Forward moves
  if (s === 'applied') {
    items.push({ label: 'Move to Prescanned', icon: 'pi pi-arrow-right', command: () => confirmRowStatus(c, 'prescanned') })
  }
  if (s === 'prescanned' && props.interviewEnabled) {
    items.push({ label: 'Move to Interviewed', icon: 'pi pi-arrow-right', command: () => confirmRowStatus(c, 'interviewed') })
  }
  if (s !== 'shortlisted' && s !== 'hired' && s !== 'archived') {
    items.push({ label: 'Shortlist', icon: 'pi pi-star', command: () => confirmRowStatus(c, 'shortlisted') })
  }
  if (s !== 'hired' && s !== 'archived') {
    items.push({ label: 'Hire', icon: 'pi pi-check-circle', command: () => confirmRowStatus(c, 'hired') })
  }

  // Reject
  if (s !== 'rejected' && s !== 'hired' && s !== 'archived') {
    items.push({ label: '', icon: '', command: () => {}, separator: true })
    items.push({ label: 'Reject', icon: 'pi pi-times', command: () => confirmRowStatus(c, 'rejected') })
  }

  // Archive
  if (s === 'rejected' || s === 'expired' || s === 'shortlisted' || s === 'hired') {
    items.push({ label: 'Archive', icon: 'pi pi-inbox', command: () => confirmRowStatus(c, 'archived') })
  }

  // Reset
  if (s !== 'applied' && s !== 'archived') {
    items.push({ label: 'Reset to Applied', icon: 'pi pi-refresh', command: () => confirmRowStatus(c, 'applied') })
  }
  if (s === 'archived') {
    items.push({ label: 'Restore to Applied', icon: 'pi pi-refresh', command: () => confirmRowStatus(c, 'applied') })
  }

  return items
}

function confirmRowStatus(c: Application, toStatus: ApplicationStatus): void {
  const label = toStatus.replace(/_/g, ' ')
  confirm.require({
    message: `Move ${c.candidateName} to "${label}"?`,
    header: 'Change Status',
    icon: toStatus === 'rejected' ? 'pi pi-exclamation-triangle' : 'pi pi-question-circle',
    acceptClass: toStatus === 'rejected' ? 'p-button-danger' : '',
    acceptLabel: 'Yes',
    rejectLabel: 'Cancel',
    accept: async () => {
      await candidateStore.updateStatus(c.id, toStatus).catch(() => {})
    },
  })
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

// --- Kanban handlers ---

function handleKanbanStatusChange(candidateId: string, status: ApplicationStatus): void {
  const candidate = candidateStore.candidates.find((c) => c.id === candidateId)
  if (!candidate) return

  const statusLabel = status.replace(/_/g, ' ')
  const isReset = status === 'applied'
  const message = isReset
    ? `Reset ${candidate.candidateName} back to "Applied"?`
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

function handleBatchMove(fromStatus: ApplicationStatus, toStatus: ApplicationStatus): void {
  const count = candidateStore.candidates.filter((c) => c.status === fromStatus).length
  if (!count) return

  confirm.require({
    message: `Move all ${count} "${fromStatus}" candidate(s) to "${toStatus}"?`,
    header: 'Batch Move',
    icon: 'pi pi-arrows-alt',
    acceptLabel: 'Yes, move all',
    rejectLabel: 'Cancel',
    accept: async () => {
      await candidateService.batchMove(props.vacancyId, {
        fromStatus,
        toStatus,
      })
      fetchCandidates()
    },
  })
}

function handleBatchMoveByScore(
  fromStatus: ApplicationStatus,
  toStatus: ApplicationStatus,
  scoreField: string,
  threshold: number,
  direction: 'below' | 'above',
): void {
  const dirLabel = direction === 'below' ? '<' : '>'
  const fieldLabel = scoreField === 'match_score' ? 'CV match' : scoreField === 'prescanning_score' ? 'prescan score' : 'interview score'

  confirm.require({
    message: `Move "${fromStatus}" candidates with ${fieldLabel} ${dirLabel} ${threshold} to "${toStatus}"?`,
    header: 'Batch Move by Score',
    icon: 'pi pi-filter',
    acceptLabel: 'Yes, move',
    rejectLabel: 'Cancel',
    accept: async () => {
      await candidateService.batchMove(props.vacancyId, {
        fromStatus,
        toStatus,
        scoreField: scoreField as 'match_score' | 'prescanning_score' | 'interview_score',
        ...(direction === 'below' ? { maxScore: threshold } : { minScore: threshold }),
      })
      fetchCandidates()
    },
  })
}

function handleBatchMoveNoCv(fromStatus: ApplicationStatus, toStatus: ApplicationStatus): void {
  confirm.require({
    message: `Move all "${fromStatus}" candidates without CV to "${toStatus}"?`,
    header: 'Batch Move (No CV)',
    icon: 'pi pi-file',
    acceptLabel: 'Yes, move',
    rejectLabel: 'Cancel',
    accept: async () => {
      await candidateService.batchMove(props.vacancyId, {
        fromStatus,
        toStatus,
        hasCv: false,
      })
      fetchCandidates()
    },
  })
}

function handleBatchMoveByDays(fromStatus: ApplicationStatus, toStatus: ApplicationStatus, days: number): void {
  confirm.require({
    message: `Move "${fromStatus}" candidates idle for more than ${days} days to "${toStatus}"?`,
    header: 'Batch Move (Idle)',
    icon: 'pi pi-clock',
    acceptLabel: 'Yes, move',
    rejectLabel: 'Cancel',
    accept: async () => {
      await candidateService.batchMove(props.vacancyId, {
        fromStatus,
        toStatus,
        daysSinceApplied: days,
      })
      fetchCandidates()
    },
  })
}

function handleSoftDeleteAll(status: ApplicationStatus): void {
  const candidates = candidateStore.candidates.filter((c) => c.status === status)
  if (!candidates.length) return

  confirm.require({
    message: `Permanently hide all ${candidates.length} archived candidate(s)? They will no longer appear anywhere.`,
    header: 'Clear Archive',
    icon: 'pi pi-trash',
    acceptClass: 'p-button-danger',
    acceptLabel: 'Yes, clear all',
    rejectLabel: 'Cancel',
    accept: async () => {
      const ids = candidates.map((c) => c.id)
      await candidateService.softDelete(ids)
      fetchCandidates()
    },
  })
}
</script>

<template>
  <div class="space-y-3 py-3 sm:py-4">
    <!-- Toolbar: single row -->
    <div class="flex items-center gap-2">
      <!-- View toggle -->
      <div class="flex shrink-0 items-center rounded-lg border border-gray-200 p-0.5">
        <button
          class="rounded-md px-2.5 py-1 text-xs font-medium transition-colors sm:px-3 sm:py-1.5 sm:text-sm"
          :class="candidateViewMode === 'kanban' ? 'bg-gray-900 text-white' : 'text-gray-500 hover:text-gray-700'"
          @click="candidateViewMode = 'kanban'"
        >
          <i class="pi pi-th-large sm:mr-1.5"></i><span class="hidden sm:inline">Board</span>
        </button>
        <button
          class="rounded-md px-2.5 py-1 text-xs font-medium transition-colors sm:px-3 sm:py-1.5 sm:text-sm"
          :class="candidateViewMode === 'table' ? 'bg-gray-900 text-white' : 'text-gray-500 hover:text-gray-700'"
          @click="candidateViewMode = 'table'"
        >
          <i class="pi pi-list sm:mr-1.5"></i><span class="hidden sm:inline">Table</span>
        </button>
      </div>

      <!-- Search -->
      <IconField class="min-w-0 flex-1 sm:max-w-64">
        <InputIcon class="pi pi-search" />
        <InputText
          v-model="searchQuery"
          :placeholder="t('common.search')"
          class="w-full"
          @input="onSearchInput"
        />
      </IconField>

      <!-- Table-only filters -->
      <template v-if="candidateViewMode === 'table'">
        <Dropdown
          v-model="statusFilter"
          :options="statusOptions"
          option-label="label"
          option-value="value"
          :placeholder="t('common.status')"
          class="hidden shrink-0 sm:flex"
        />
        <Dropdown
          v-model="orderingFilter"
          :options="orderingOptions"
          option-label="label"
          option-value="value"
          placeholder="Sort"
          class="hidden shrink-0 sm:flex"
        />
      </template>

      <!-- Bulk actions (when selected) -->
      <template v-if="selectedCandidates.length > 0">
        <span class="hidden shrink-0 text-xs text-gray-500 sm:inline">{{ selectedCandidates.length }} selected</span>
        <Dropdown
          :model-value="null"
          :options="bulkActionOptions"
          option-label="label"
          option-value="value"
          placeholder="Bulk Actions"
          class="shrink-0"
          @change="handleBulkAction"
        />
      </template>

      <!-- Count -->
      <span class="ml-auto shrink-0 text-xs text-gray-400">{{ candidateStore.candidates.length }}</span>
    </div>

    <p v-if="candidateStore.error" class="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-600">
      {{ candidateStore.error }}
    </p>

    <!-- Kanban View -->
    <CandidateKanban
      v-if="candidateViewMode === 'kanban'"
      :candidates="candidateStore.candidates"
      :loading="candidateStore.loading"
      :interview-enabled="interviewEnabled"
      @status-change="handleKanbanStatusChange"
      @batch-move="handleBatchMove"
      @batch-move-by-score="handleBatchMoveByScore"
      @batch-move-no-cv="handleBatchMoveNoCv"
      @batch-move-by-days="handleBatchMoveByDays"
      @soft-delete-all="handleSoftDeleteAll"
    />

    <!-- Table View -->
    <DataTable
      v-if="candidateViewMode === 'table'"
      v-model:selection="selectedCandidates"
      :value="candidateStore.candidates"
      :loading="candidateStore.loading"
      row-hover
      data-key="id"
      scrollable
      class="text-sm"
    >
      <Column selection-mode="multiple" header-style="width: 3rem" />

      <!-- Candidate -->
      <Column :header="t('candidates.title')" sortable sort-field="candidateName" style="min-width: 200px">
        <template #body="{ data }">
          <div
            class="flex cursor-pointer items-center gap-2.5"
            @click="viewCandidateDetail(data as Application)"
          >
            <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-50 text-xs font-semibold text-blue-700">
              {{ (data as Application).candidateName.split(' ').map((n: string) => n[0]).slice(0, 2).join('').toUpperCase() }}
            </div>
            <div class="min-w-0">
              <p class="truncate font-medium text-gray-900">{{ (data as Application).candidateName }}</p>
              <p class="truncate text-xs text-gray-500">{{ (data as Application).candidateEmail }}</p>
            </div>
          </div>
        </template>
      </Column>

      <!-- Status -->
      <Column :header="t('common.status')" sortable sort-field="status" style="min-width: 120px">
        <template #body="{ data }">
          <ApplicationStatusBadge :status="(data as Application).status" />
        </template>
      </Column>

      <!-- Overall -->
      <Column :header="t('candidates.overallScore')" sortable sort-field="matchScore" style="min-width: 80px">
        <template #body="{ data }">
          <span
            v-if="getTableOverallScore(data as Application) != null"
            class="inline-flex h-7 w-7 items-center justify-center rounded-full border-2 text-xs font-bold"
            :class="getTableScoreClasses(getTableOverallScore(data as Application)!)"
          >
            {{ getTableOverallScore(data as Application) }}
          </span>
          <span v-else class="text-xs text-gray-400">—</span>
        </template>
      </Column>

      <!-- CV Match -->
      <Column header="CV" sortable sort-field="matchScore" style="min-width: 70px">
        <template #body="{ data }">
          <span
            v-if="(data as Application).matchScore !== null"
            class="rounded px-1.5 py-0.5 text-xs font-medium bg-blue-50 text-blue-700"
          >
            {{ (data as Application).matchScore }}%
          </span>
          <span v-else class="text-xs text-gray-400">—</span>
        </template>
      </Column>

      <!-- Prescan -->
      <Column :header="t('candidates.prescanScore')" style="min-width: 80px">
        <template #body="{ data }">
          <span
            v-if="(data as Application).prescanningScore != null"
            class="rounded px-1.5 py-0.5 text-xs font-medium"
            :class="getTableScoreBadge((data as Application).prescanningScore!, 10)"
          >
            {{ (data as Application).prescanningScore }}/10
          </span>
          <span v-else class="text-xs text-gray-400">—</span>
        </template>
      </Column>

      <!-- Interview (conditional) -->
      <Column v-if="interviewEnabled" :header="t('candidates.interviewScore')" style="min-width: 80px">
        <template #body="{ data }">
          <span
            v-if="(data as Application).interviewScore != null"
            class="rounded px-1.5 py-0.5 text-xs font-medium"
            :class="getTableScoreBadge((data as Application).interviewScore!, 10)"
          >
            {{ (data as Application).interviewScore }}/10
          </span>
          <span v-else class="text-xs text-gray-400">—</span>
        </template>
      </Column>

      <!-- Applied date -->
      <Column :header="t('candidates.status.applied')" sortable sort-field="createdAt" style="min-width: 100px">
        <template #body="{ data }">
          <span class="text-xs text-gray-500">{{ formatDate((data as Application).createdAt) }}</span>
        </template>
      </Column>

      <!-- Row actions -->
      <Column header="" style="width: 50px" :exportable="false">
        <template #body="{ data }">
          <button
            class="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            @click.stop="toggleRowMenu($event, (data as Application).id)"
          >
            <i class="pi pi-ellipsis-v text-sm"></i>
          </button>
          <Menu
            :ref="(el: unknown) => setRowMenuRef((data as Application).id, el)"
            :model="getRowMenuItems(data as Application)"
            :popup="true"
          />
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
  </div>
</template>
