<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Menu from 'primevue/menu'
import Dialog from 'primevue/dialog'
import InputNumber from 'primevue/inputnumber'
import Button from 'primevue/button'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Application, ApplicationStatus } from '../types/candidate.types'

const props = defineProps<{
  candidates: Application[]
  loading: boolean
  interviewEnabled?: boolean
}>()

const emit = defineEmits<{
  statusChange: [id: string, status: ApplicationStatus]
  batchMove: [fromStatus: ApplicationStatus, toStatus: ApplicationStatus]
  batchMoveByScore: [fromStatus: ApplicationStatus, toStatus: ApplicationStatus, scoreField: string, threshold: number, direction: 'below' | 'above']
  batchMoveNoCv: [fromStatus: ApplicationStatus, toStatus: ApplicationStatus]
  batchMoveByDays: [fromStatus: ApplicationStatus, toStatus: ApplicationStatus, days: number]
  softDeleteAll: [status: ApplicationStatus]
}>()

const router = useRouter()

interface KanbanColumn {
  status: ApplicationStatus
  label: string
  color: string
  bgColor: string
  borderColor: string
  dotColor: string
}

const columns: KanbanColumn[] = [
  { status: 'applied', label: 'Applied', color: 'text-blue-700', bgColor: 'bg-blue-50', borderColor: 'border-blue-200', dotColor: 'bg-blue-500' },
  { status: 'prescanned', label: 'Prescanned', color: 'text-teal-700', bgColor: 'bg-teal-50', borderColor: 'border-teal-200', dotColor: 'bg-teal-500' },
  { status: 'interviewed', label: 'Interviewed', color: 'text-emerald-700', bgColor: 'bg-emerald-50', borderColor: 'border-emerald-200', dotColor: 'bg-emerald-500' },
  { status: 'shortlisted', label: 'Shortlisted', color: 'text-violet-700', bgColor: 'bg-violet-50', borderColor: 'border-violet-200', dotColor: 'bg-violet-500' },
  { status: 'hired', label: 'Hired', color: 'text-green-700', bgColor: 'bg-green-50', borderColor: 'border-green-200', dotColor: 'bg-green-500' },
  { status: 'rejected', label: 'Rejected', color: 'text-red-700', bgColor: 'bg-red-50', borderColor: 'border-red-200', dotColor: 'bg-red-500' },
  { status: 'archived', label: 'Archived', color: 'text-gray-600', bgColor: 'bg-gray-100', borderColor: 'border-gray-200', dotColor: 'bg-gray-400' },
]

const visibleColumns = computed(() =>
  props.interviewEnabled
    ? columns
    : columns.filter((c) => c.status !== 'interviewed'),
)

// --- Column menu ---
const columnMenuRefs = ref<Record<string, InstanceType<typeof Menu> | null>>({})

function setMenuRef(status: string, el: unknown) {
  columnMenuRefs.value[status] = el as InstanceType<typeof Menu> | null
}

function toggleColumnMenu(event: Event, status: string) {
  columnMenuRefs.value[status]?.toggle(event)
}

function getColumnMenuItems(status: ApplicationStatus) {
  const items: { label: string; icon: string; command: () => void; separator?: boolean }[] = []
  const count = columnCounts.value[status]
  if (count === 0) return [{ label: 'No candidates', icon: 'pi pi-info-circle', command: () => {} }]

  if (status === 'applied') {
    items.push({ label: 'Reject all', icon: 'pi pi-times', command: () => emit('batchMove', 'applied', 'rejected') })
    items.push({ label: 'Reject by CV match < ...', icon: 'pi pi-filter', command: () => openThresholdDialog('applied', 'rejected', 'match_score', 'below') })
    items.push({ label: 'Reject with no CV', icon: 'pi pi-file', command: () => emit('batchMoveNoCv', 'applied', 'rejected') })
    items.push({ label: 'Reject idle > ... days', icon: 'pi pi-clock', command: () => openDaysDialog('applied', 'rejected') })
    items.push({ label: '', icon: '', command: () => {}, separator: true })
    items.push({ label: 'Shortlist all', icon: 'pi pi-star', command: () => emit('batchMove', 'applied', 'shortlisted') })
    items.push({ label: 'Hire all', icon: 'pi pi-check-circle', command: () => emit('batchMove', 'applied', 'hired') })
    items.push({ label: 'Archive all', icon: 'pi pi-inbox', command: () => emit('batchMove', 'applied', 'archived') })
  }

  if (status === 'prescanned') {
    if (props.interviewEnabled) {
      items.push({ label: 'Move all to Interviewed', icon: 'pi pi-arrow-right', command: () => emit('batchMove', 'prescanned', 'interviewed') })
    }
    items.push({ label: 'Shortlist all', icon: 'pi pi-star', command: () => emit('batchMove', 'prescanned', 'shortlisted') })
    items.push({ label: 'Hire all', icon: 'pi pi-check-circle', command: () => emit('batchMove', 'prescanned', 'hired') })
    items.push({ label: '', icon: '', command: () => {}, separator: true })
    items.push({ label: 'Reject all', icon: 'pi pi-times', command: () => emit('batchMove', 'prescanned', 'rejected') })
    items.push({ label: 'Reject by prescan score < ...', icon: 'pi pi-filter', command: () => openThresholdDialog('prescanned', 'rejected', 'prescanning_score', 'below') })
    items.push({ label: 'Shortlist by prescan score > ...', icon: 'pi pi-filter', command: () => openThresholdDialog('prescanned', 'shortlisted', 'prescanning_score', 'above') })
    items.push({ label: 'Archive all', icon: 'pi pi-inbox', command: () => emit('batchMove', 'prescanned', 'archived') })
  }

  if (status === 'interviewed') {
    items.push({ label: 'Shortlist all', icon: 'pi pi-star', command: () => emit('batchMove', 'interviewed', 'shortlisted') })
    items.push({ label: 'Hire all', icon: 'pi pi-check-circle', command: () => emit('batchMove', 'interviewed', 'hired') })
    items.push({ label: '', icon: '', command: () => {}, separator: true })
    items.push({ label: 'Reject all', icon: 'pi pi-times', command: () => emit('batchMove', 'interviewed', 'rejected') })
    items.push({ label: 'Reject by interview score < ...', icon: 'pi pi-filter', command: () => openThresholdDialog('interviewed', 'rejected', 'interview_score', 'below') })
    items.push({ label: 'Shortlist by interview score > ...', icon: 'pi pi-filter', command: () => openThresholdDialog('interviewed', 'shortlisted', 'interview_score', 'above') })
    items.push({ label: 'Archive all', icon: 'pi pi-inbox', command: () => emit('batchMove', 'interviewed', 'archived') })
  }

  if (status === 'shortlisted') {
    items.push({ label: 'Hire all', icon: 'pi pi-check-circle', command: () => emit('batchMove', 'shortlisted', 'hired') })
    items.push({ label: 'Reject all', icon: 'pi pi-times', command: () => emit('batchMove', 'shortlisted', 'rejected') })
    items.push({ label: 'Archive all', icon: 'pi pi-inbox', command: () => emit('batchMove', 'shortlisted', 'archived') })
  }

  if (status === 'hired') {
    items.push({ label: 'Archive all', icon: 'pi pi-inbox', command: () => emit('batchMove', 'hired', 'archived') })
  }

  if (status === 'rejected') {
    items.push({ label: 'Archive all', icon: 'pi pi-inbox', command: () => emit('batchMove', 'rejected', 'archived') })
    items.push({ label: 'Reset all to Applied', icon: 'pi pi-refresh', command: () => emit('batchMove', 'rejected', 'applied') })
  }

  if (status === 'archived') {
    items.push({ label: 'Restore all to Applied', icon: 'pi pi-refresh', command: () => emit('batchMove', 'archived', 'applied') })
    items.push({ label: 'Clear all (soft delete)', icon: 'pi pi-trash', command: () => emit('softDeleteAll', 'archived') })
  }

  return items
}

// --- Threshold dialog ---
const showThresholdDialog = ref(false)
const thresholdValue = ref<number | null>(null)
const thresholdContext = ref<{
  fromStatus: ApplicationStatus
  toStatus: ApplicationStatus
  scoreField: string
  direction: 'below' | 'above'
}>({ fromStatus: 'applied', toStatus: 'rejected', scoreField: 'match_score', direction: 'below' })

function openThresholdDialog(from: ApplicationStatus, to: ApplicationStatus, field: string, dir: 'below' | 'above') {
  thresholdContext.value = { fromStatus: from, toStatus: to, scoreField: field, direction: dir }
  thresholdValue.value = dir === 'below' ? 4 : 7
  showThresholdDialog.value = true
}

function confirmThreshold() {
  if (thresholdValue.value == null) return
  const ctx = thresholdContext.value
  emit('batchMoveByScore', ctx.fromStatus, ctx.toStatus, ctx.scoreField, thresholdValue.value, ctx.direction)
  showThresholdDialog.value = false
}

const thresholdDialogTitle = computed(() => {
  const ctx = thresholdContext.value
  const fieldLabel = ctx.scoreField === 'match_score' ? 'CV match' : ctx.scoreField === 'prescanning_score' ? 'prescanning score' : 'interview score'
  const dirLabel = ctx.direction === 'below' ? 'below' : 'above'
  return `${ctx.toStatus === 'rejected' ? 'Reject' : 'Shortlist'} where ${fieldLabel} ${dirLabel}...`
})

const thresholdMax = computed(() => thresholdContext.value.scoreField === 'match_score' ? 100 : 10)

// --- Days dialog ---
const showDaysDialog = ref(false)
const daysValue = ref<number | null>(7)
const daysContext = ref<{ fromStatus: ApplicationStatus; toStatus: ApplicationStatus }>({ fromStatus: 'applied', toStatus: 'rejected' })

function openDaysDialog(from: ApplicationStatus, to: ApplicationStatus) {
  daysContext.value = { fromStatus: from, toStatus: to }
  daysValue.value = 7
  showDaysDialog.value = true
}

function confirmDays() {
  if (daysValue.value == null) return
  emit('batchMoveByDays', daysContext.value.fromStatus, daysContext.value.toStatus, daysValue.value)
  showDaysDialog.value = false
}

// --- Standard kanban logic ---
function getCandidatesForColumn(status: ApplicationStatus): Application[] {
  return props.candidates.filter((c) => c.status === status)
}

const columnCounts = computed(() => {
  const counts: Record<string, number> = {}
  for (const col of columns) {
    counts[col.status] = getCandidatesForColumn(col.status).length
  }
  return counts
})

function viewCandidate(candidate: Application): void {
  router.push({ name: ROUTE_NAMES.CANDIDATE_DETAIL, params: { id: candidate.id } })
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n.charAt(0))
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString([], { month: 'short', day: 'numeric' })
}

function getOverallScore(c: Application): number | null {
  const cv = c.matchScore != null ? Number(c.matchScore) : null
  const ps = c.prescanningScore != null ? Number(c.prescanningScore) * 10 : null // normalize to 0-100
  const iv = c.interviewScore != null ? Number(c.interviewScore) * 10 : null

  if (cv != null && ps != null && iv != null) return Math.round(cv * 0.2 + ps * 0.3 + iv * 0.5)
  if (cv != null && ps != null) return Math.round(cv * 0.4 + ps * 0.6)
  if (ps != null && iv != null) return Math.round(ps * 0.4 + iv * 0.6)
  if (cv != null) return Math.round(cv)
  if (ps != null) return Math.round(ps)
  if (iv != null) return Math.round(iv)
  return null
}

function getScoreColor(score: number): string {
  if (score >= 70) return 'text-emerald-600'
  if (score >= 45) return 'text-amber-600'
  return 'text-red-500'
}

function getScoreRingColor(score: number): string {
  if (score >= 70) return 'border-emerald-400'
  if (score >= 45) return 'border-amber-400'
  return 'border-red-400'
}

function onDragStart(event: DragEvent, candidate: Application): void {
  event.dataTransfer?.setData('candidateId', candidate.id)
}

function onDrop(event: DragEvent, status: ApplicationStatus): void {
  const candidateId = event.dataTransfer?.getData('candidateId')
  if (candidateId) {
    emit('statusChange', candidateId, status)
  }
}

function onDragOver(event: DragEvent): void {
  event.preventDefault()
}
</script>

<template>
  <div v-if="loading" class="flex items-center justify-center py-20">
    <i class="pi pi-spinner pi-spin text-3xl text-gray-300"></i>
  </div>

  <div v-else class="flex gap-3 overflow-x-auto pb-4 sm:gap-4">
    <div
      v-for="column in visibleColumns"
      :key="column.status"
      class="flex w-56 shrink-0 flex-col rounded-xl border border-gray-100 bg-gray-50/50 sm:w-64"
      @drop="onDrop($event, column.status)"
      @dragover="onDragOver"
    >
      <!-- Column header -->
      <div class="flex items-center justify-between px-4 py-3">
        <div class="flex items-center gap-2">
          <div class="h-2 w-2 rounded-full" :class="column.dotColor"></div>
          <span class="text-sm font-semibold text-gray-700">{{ column.label }}</span>
          <span
            class="flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-xs font-medium"
            :class="[column.bgColor, column.color]"
          >
            {{ columnCounts[column.status] }}
          </span>
        </div>
        <button
          class="rounded p-1 text-gray-400 hover:bg-gray-200 hover:text-gray-600"
          @click="toggleColumnMenu($event, column.status)"
        >
          <i class="pi pi-ellipsis-v text-xs"></i>
        </button>
        <Menu
          :ref="(el: unknown) => setMenuRef(column.status, el)"
          :model="getColumnMenuItems(column.status)"
          :popup="true"
        />
      </div>

      <!-- Cards -->
      <div class="flex flex-1 flex-col gap-2 px-3 pb-3" style="min-height: 120px">
        <div
          v-for="candidate in getCandidatesForColumn(column.status)"
          :key="candidate.id"
          draggable="true"
          class="cursor-pointer rounded-lg border border-gray-100 bg-white p-3 shadow-sm transition-all hover:shadow-md"
          @click="viewCandidate(candidate)"
          @dragstart="onDragStart($event, candidate)"
        >
          <!-- Top: avatar + name + overall score ring -->
          <div class="flex items-start gap-2.5">
            <div
              class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold"
              :class="[column.bgColor, column.color]"
            >
              {{ getInitials(candidate.candidateName) }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-medium text-gray-900">
                {{ candidate.candidateName }}
              </p>
              <p class="truncate text-xs text-gray-500">
                {{ candidate.candidateEmail }}
              </p>
            </div>
            <!-- Overall score ring -->
            <div
              v-if="getOverallScore(candidate) != null"
              class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border-2 text-xs font-bold"
              :class="[getScoreColor(getOverallScore(candidate)!), getScoreRingColor(getOverallScore(candidate)!)]"
              :title="`Overall score: ${getOverallScore(candidate)}%`"
            >
              {{ getOverallScore(candidate) }}
            </div>
            <div
              v-else-if="candidate.cvFile && candidate.matchScore === null"
              class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border-2 border-gray-200"
              title="Processing..."
            >
              <i class="pi pi-spinner pi-spin text-xs text-gray-400"></i>
            </div>
          </div>

          <!-- Middle: date -->
          <div class="mt-2 flex items-center text-xs text-gray-400">
            <i class="pi pi-calendar mr-1" style="font-size: 9px"></i>
            {{ formatDate(candidate.createdAt) }}
          </div>

          <!-- Bottom: individual score badges -->
          <div
            v-if="candidate.matchScore !== null || candidate.prescanningScore != null || candidate.interviewScore != null"
            class="mt-2 flex flex-wrap gap-1"
          >
            <span
              v-if="candidate.matchScore !== null"
              class="inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 text-[10px] font-medium bg-blue-50 text-blue-700"
              title="CV match score"
            >
              CV {{ candidate.matchScore }}%
            </span>
            <span
              v-if="candidate.prescanningScore != null"
              class="inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 text-[10px] font-medium"
              :class="
                candidate.prescanningScore >= 7
                  ? 'bg-teal-50 text-teal-700'
                  : candidate.prescanningScore >= 5
                    ? 'bg-amber-50 text-amber-700'
                    : 'bg-red-50 text-red-700'
              "
              title="Prescanning score"
            >
              Prescan {{ candidate.prescanningScore }}/10
            </span>
            <span
              v-if="candidate.interviewScore != null"
              class="inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 text-[10px] font-medium"
              :class="
                candidate.interviewScore >= 7
                  ? 'bg-emerald-50 text-emerald-700'
                  : candidate.interviewScore >= 5
                    ? 'bg-amber-50 text-amber-700'
                    : 'bg-red-50 text-red-700'
              "
              title="Interview score"
            >
              Interview {{ candidate.interviewScore }}/10
            </span>
          </div>
        </div>

        <!-- Empty state -->
        <div
          v-if="getCandidatesForColumn(column.status).length === 0"
          class="flex flex-1 items-center justify-center rounded-lg border border-dashed border-gray-200 py-6"
        >
          <p class="text-xs text-gray-400">No candidates</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Threshold input dialog -->
  <Dialog v-model:visible="showThresholdDialog" :header="thresholdDialogTitle" modal :style="{ width: '360px' }">
    <div class="flex flex-col gap-3">
      <label class="text-sm text-gray-600">
        {{ thresholdContext.direction === 'below' ? 'Score below' : 'Score above' }}
      </label>
      <InputNumber v-model="thresholdValue" :min="0" :max="thresholdMax" show-buttons class="w-full" />
    </div>
    <template #footer>
      <Button label="Cancel" severity="secondary" text @click="showThresholdDialog = false" />
      <Button label="Confirm" @click="confirmThreshold" />
    </template>
  </Dialog>

  <!-- Days input dialog -->
  <Dialog v-model:visible="showDaysDialog" header="Reject idle candidates" modal :style="{ width: '360px' }">
    <div class="flex flex-col gap-3">
      <label class="text-sm text-gray-600">Applied more than ... days ago</label>
      <InputNumber v-model="daysValue" :min="1" :max="365" show-buttons suffix=" days" class="w-full" />
    </div>
    <template #footer>
      <Button label="Cancel" severity="secondary" text @click="showDaysDialog = false" />
      <Button label="Confirm" severity="danger" @click="confirmDays" />
    </template>
  </Dialog>
</template>
