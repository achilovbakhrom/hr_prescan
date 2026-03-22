<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Menu from 'primevue/menu'
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'
import { useVacancyStore } from '../stores/vacancy.store'
import VacancyStatusBadge from '../components/VacancyStatusBadge.vue'
import VacancyOverview from '../components/VacancyOverview.vue'
import VacancyForm from '../components/VacancyForm.vue'
import QuestionList from '../components/QuestionList.vue'
import CriteriaList from '../components/CriteriaList.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import { candidateService } from '@/features/candidates/services/candidate.service'
import CandidateKanban from '@/features/candidates/components/CandidateKanban.vue'
import ApplicationStatusBadge from '@/features/candidates/components/ApplicationStatusBadge.vue'
import type { Application, ApplicationStatus } from '@/shared/types/candidate.types'
import type { CreateVacancyRequest, VacancyStatus } from '../types/vacancy.types'

const route = useRoute()
const router = useRouter()
const confirm = useConfirm()
const vacancyStore = useVacancyStore()
const candidateStore = useCandidateStore()
const TAB_NAMES_BASE = ['overview', 'prescanning', 'candidates'] as const
const TAB_NAMES_WITH_INTERVIEW = ['overview', 'prescanning', 'interview', 'candidates'] as const
const tabNames = computed(() =>
  vacancy.value?.interviewEnabled ? TAB_NAMES_WITH_INTERVIEW : TAB_NAMES_BASE,
)
const candidatesTabIndex = computed(() => tabNames.value.length - 1)
const activeTab = computed({
  get: () => {
    const tab = route.query.tab as string
    const idx = (tabNames.value as readonly string[]).indexOf(tab)
    return idx >= 0 ? idx : 0
  },
  set: (val: number) => {
    router.replace({ query: { ...route.query, tab: tabNames.value[val] } })
  },
})
const vacancyId = computed(() => route.params.id as string)
const vacancy = computed(() => vacancyStore.currentVacancy)

// --- Candidates tab state ---
const candidateViewMode = ref<'kanban' | 'table'>('kanban')
const statusFilter = ref<string | undefined>(undefined)
const orderingFilter = ref<string>('-created_at')
const searchQuery = ref('')
const selectedCandidates = ref<Application[]>([])
let searchTimeout: ReturnType<typeof setTimeout> | null = null

const statusOptions = [
  { label: 'All Statuses', value: undefined },
  { label: 'Applied', value: 'applied' },
  { label: 'Prescanned', value: 'prescanned' },
  { label: 'Interviewed', value: 'interviewed' },
  { label: 'Shortlisted', value: 'shortlisted' },
  { label: 'Hired', value: 'hired' },
  { label: 'Rejected', value: 'rejected' },
  { label: 'Expired', value: 'expired' },
  { label: 'Archived', value: 'archived' },
]

const orderingOptions = [
  { label: 'Newest first', value: '-created_at' },
  { label: 'Oldest first', value: 'created_at' },
  { label: 'Highest score', value: '-match_score' },
  { label: 'Lowest score', value: 'match_score' },
]

const bulkActionOptions = [
  { label: 'Shortlist', value: 'shortlisted' as ApplicationStatus },
  { label: 'Hire', value: 'hired' as ApplicationStatus },
  { label: 'Reject', value: 'rejected' as ApplicationStatus },
  { label: 'Archive', value: 'archived' as ApplicationStatus },
  { label: 'Reset to Applied', value: 'applied' as ApplicationStatus },
]

// --- Kanban batch action handlers ---

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
      await candidateService.batchMove(vacancyId.value, {
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
      await candidateService.batchMove(vacancyId.value, {
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
      await candidateService.batchMove(vacancyId.value, {
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
      await candidateService.batchMove(vacancyId.value, {
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


function fetchCandidates(): void {
  candidateStore.fetchVacancyCandidates(vacancyId.value, {
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
  if (s === 'prescanned' && vacancy.value?.interviewEnabled) {
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

const editFormData = computed(() => {
  if (!vacancy.value) return undefined
  const v = vacancy.value
  return {
    title: v.title,
    description: v.description,
    requirements: v.requirements,
    responsibilities: v.responsibilities,
    skills: v.skills,
    salaryMin: v.salaryMin,
    salaryMax: v.salaryMax,
    salaryCurrency: v.salaryCurrency,
    location: v.location,
    isRemote: v.isRemote,
    employmentType: v.employmentType,
    experienceLevel: v.experienceLevel,
    deadline: v.deadline,
    visibility: v.visibility,
    interviewEnabled: v.interviewEnabled,
    interviewMode: v.interviewMode,
    interviewDuration: v.interviewDuration,
    prescanningPrompt: v.prescanningPrompt,
    interviewPrompt: v.interviewPrompt,
    companyInfo: v.companyInfo,
    cvRequired: v.cvRequired,
  }
})

const prescanningQuestions = computed(() =>
  vacancy.value?.questions.filter((q) => q.step === 'prescanning') ?? [],
)
const interviewQuestions = computed(() =>
  vacancy.value?.questions.filter((q) => q.step === 'interview') ?? [],
)
const prescanningCriteria = computed(() =>
  vacancy.value?.criteria.filter((c) => c.step === 'prescanning') ?? [],
)
const interviewCriteria = computed(() =>
  vacancy.value?.criteria.filter((c) => c.step === 'interview') ?? [],
)

onMounted(() => {
  vacancyStore.fetchVacancyDetail(vacancyId.value)
  fetchCandidates()
})

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

const linkCopied = ref(false)

function copyShareLink(): void {
  if (!vacancy.value) return
  const url = `${window.location.origin}/jobs/share/${vacancy.value.shareToken}`
  navigator.clipboard.writeText(url).then(() => {
    linkCopied.value = true
    setTimeout(() => { linkCopied.value = false }, 2000)
  })
}

async function handleStatusChange(status: VacancyStatus): Promise<void> {
  await vacancyStore.changeStatus(vacancyId.value, status).catch(() => {})
}

async function handleUpdate(data: CreateVacancyRequest): Promise<void> {
  try {
    await vacancyStore.updateVacancy(vacancyId.value, data)
  } catch {
    /* store handles error */
  }
}
</script>

<template>
  <div class="space-y-3 sm:space-y-4">
    <!-- Header -->
    <div class="flex items-center gap-2 sm:gap-3">
      <button
        class="shrink-0 rounded-lg p-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
        @click="router.push({ name: ROUTE_NAMES.VACANCY_LIST })"
      >
        <i class="pi pi-arrow-left"></i>
      </button>
      <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-2">
          <h1 class="truncate text-base font-bold sm:text-lg md:text-2xl">
            {{ vacancy?.title ?? 'Loading...' }}
          </h1>
          <VacancyStatusBadge v-if="vacancy" :status="vacancy.status" />
        </div>
      </div>
    </div>

    <p v-if="vacancyStore.error" class="text-sm text-red-600">
      {{ vacancyStore.error }}
    </p>

    <div v-if="!vacancy && vacancyStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <template v-else-if="vacancy">
      <!-- Action buttons: draft → published ↔ paused → archived -->
      <div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
        <Button
          v-if="vacancy.status === 'draft'"
          label="Publish"
          icon="pi pi-send"
          size="small"
          @click="handleStatusChange('published')"
        />
        <Button
          v-if="vacancy.status === 'published'"
          label="Pause"
          icon="pi pi-pause"
          severity="warn"
          size="small"
          @click="handleStatusChange('paused')"
        />
        <Button
          v-if="vacancy.status === 'paused'"
          label="Resume"
          icon="pi pi-play"
          severity="success"
          size="small"
          @click="handleStatusChange('published')"
        />
        <Button
          v-if="vacancy.status === 'published' || vacancy.status === 'paused'"
          label="Archive"
          icon="pi pi-inbox"
          severity="secondary"
          size="small"
          outlined
          @click="handleStatusChange('archived')"
        />
        <Button
          :label="linkCopied ? 'Copied!' : 'Copy Link'"
          :icon="linkCopied ? 'pi pi-check' : 'pi pi-link'"
          :severity="linkCopied ? 'success' : 'secondary'"
          size="small"
          outlined
          @click="copyShareLink"
        />
      </div>

      <!-- Tabs -->
      <TabView v-model:activeIndex="activeTab" scrollable>
        <TabPanel value="0">
          <template #header>
            <span class="text-xs sm:text-sm">Overview</span>
          </template>
          <div class="space-y-4 py-3 sm:py-4">
            <VacancyOverview :vacancy="vacancy" />
            <hr class="border-gray-200" />
            <VacancyForm
              :initial-data="editFormData"
              :loading="vacancyStore.loading"
              @save="handleUpdate"
            />
          </div>
        </TabPanel>

        <!-- Prescanning tab: sub-tabs for questions & criteria -->
        <TabPanel value="1">
          <template #header>
            <span class="text-xs sm:text-sm"><i class="pi pi-comments mr-1"></i>Prescanning</span>
          </template>
          <div class="py-3 sm:py-4">
            <TabView>
              <TabPanel value="0">
                <template #header>
                  <span class="text-xs sm:text-sm"><i class="pi pi-list mr-1"></i>Questions</span>
                </template>
                <div class="py-3">
                  <QuestionList
                    :questions="prescanningQuestions"
                    :loading="vacancyStore.loading"
                    @add="(d) => vacancyStore.addQuestion(vacancyId, { ...d, step: 'prescanning' })"
                    @update="(qId, d) => vacancyStore.updateQuestion(vacancyId, qId, d)"
                    @delete="(qId) => vacancyStore.deleteQuestion(vacancyId, qId)"
                    @generate="() => vacancyStore.generateQuestions(vacancyId)"
                  />
                </div>
              </TabPanel>
              <TabPanel value="1">
                <template #header>
                  <span class="text-xs sm:text-sm"><i class="pi pi-chart-bar mr-1"></i>Criteria</span>
                </template>
                <div class="py-3">
                  <CriteriaList
                    :criteria="prescanningCriteria"
                    :loading="vacancyStore.loading"
                    @add="(d) => vacancyStore.addCriteria(vacancyId, { ...d, step: 'prescanning' })"
                    @update="(cId, d) => vacancyStore.updateCriteria(vacancyId, cId, d)"
                    @delete="(cId) => vacancyStore.deleteCriteria(vacancyId, cId)"
                  />
                </div>
              </TabPanel>
            </TabView>
          </div>
        </TabPanel>

        <!-- Interview tab: sub-tabs for questions & criteria (only when enabled) -->
        <TabPanel v-if="vacancy.interviewEnabled" value="2">
          <template #header>
            <span class="text-xs sm:text-sm"><i class="pi pi-video mr-1"></i>Interview</span>
          </template>
          <div class="py-3 sm:py-4">
            <TabView>
              <TabPanel value="0">
                <template #header>
                  <span class="text-xs sm:text-sm"><i class="pi pi-list mr-1"></i>Questions</span>
                </template>
                <div class="py-3">
                  <QuestionList
                    :questions="interviewQuestions"
                    :loading="vacancyStore.loading"
                    @add="(d) => vacancyStore.addQuestion(vacancyId, { ...d, step: 'interview' })"
                    @update="(qId, d) => vacancyStore.updateQuestion(vacancyId, qId, d)"
                    @delete="(qId) => vacancyStore.deleteQuestion(vacancyId, qId)"
                    @generate="() => vacancyStore.generateQuestions(vacancyId)"
                  />
                </div>
              </TabPanel>
              <TabPanel value="1">
                <template #header>
                  <span class="text-xs sm:text-sm"><i class="pi pi-chart-bar mr-1"></i>Criteria</span>
                </template>
                <div class="py-3">
                  <CriteriaList
                    :criteria="interviewCriteria"
                    :loading="vacancyStore.loading"
                    @add="(d) => vacancyStore.addCriteria(vacancyId, { ...d, step: 'interview' })"
                    @update="(cId, d) => vacancyStore.updateCriteria(vacancyId, cId, d)"
                    @delete="(cId) => vacancyStore.deleteCriteria(vacancyId, cId)"
                  />
                </div>
              </TabPanel>
            </TabView>
          </div>
        </TabPanel>

        <!-- Candidates tab (always last) -->
        <TabPanel :value="String(candidatesTabIndex)">
          <template #header>
            <span class="text-xs sm:text-sm">Candidates</span>
            <span
              v-if="candidateStore.candidates.length"
              class="ml-1.5 inline-flex h-4 min-w-4 items-center justify-center rounded-full bg-blue-500 px-1 text-[9px] font-bold text-white sm:h-5 sm:min-w-5 sm:px-1.5 sm:text-[10px]"
            >
              {{ candidateStore.candidates.length }}
            </span>
          </template>
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
                  placeholder="Search..."
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
                  placeholder="Status"
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
              :interview-enabled="vacancy?.interviewEnabled ?? false"
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
              <Column header="Candidate" sortable sort-field="candidateName" style="min-width: 200px">
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
              <Column header="Status" sortable sort-field="status" style="min-width: 120px">
                <template #body="{ data }">
                  <ApplicationStatusBadge :status="(data as Application).status" />
                </template>
              </Column>

              <!-- Overall -->
              <Column header="Overall" sortable sort-field="matchScore" style="min-width: 80px">
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
              <Column header="Prescan" style="min-width: 80px">
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
              <Column v-if="vacancy?.interviewEnabled" header="Interview" style="min-width: 80px">
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
              <Column header="Applied" sortable sort-field="createdAt" style="min-width: 100px">
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
        </TabPanel>
      </TabView>
    </template>

    <ConfirmDialog />
  </div>
</template>

<style scoped>
:deep(.p-tabview-panels) {
  border-top: none !important;
  background: white !important;
  border-radius: 0 0 0.5rem 0.5rem !important;
}

:deep(.p-tabview-tablist) {
  border-width: 0 0 1px 0 !important;
  border-color: #e5e7eb !important;
}

:deep(.p-tabview-tab-header) {
  border: none !important;
  padding: 0.5rem 0.75rem !important;
}

@media (min-width: 640px) {
  :deep(.p-tabview-tab-header) {
    padding: 0.75rem 1rem !important;
  }
}
</style>
