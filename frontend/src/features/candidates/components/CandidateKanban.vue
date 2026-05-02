<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Dialog from 'primevue/dialog'
import InputNumber from 'primevue/inputnumber'
import Button from 'primevue/button'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import KanbanColumn from './KanbanColumn.vue'
import type { ColumnDef } from './KanbanColumn.vue'
import type { Application, ApplicationStatus } from '../types/candidate.types'
import { buildColumnMenuItems } from '../composables/useKanbanMenuItems'

const props = defineProps<{
  candidates: Application[]
  loading: boolean
  interviewEnabled?: boolean
}>()
const emit = defineEmits<{
  statusChange: [id: string, status: ApplicationStatus]
  batchMove: [fromStatus: ApplicationStatus, toStatus: ApplicationStatus]
  batchMoveByScore: [
    fromStatus: ApplicationStatus,
    toStatus: ApplicationStatus,
    scoreField: string,
    threshold: number,
    direction: 'below' | 'above',
  ]
  batchMoveNoCv: [fromStatus: ApplicationStatus, toStatus: ApplicationStatus]
  batchMoveByDays: [fromStatus: ApplicationStatus, toStatus: ApplicationStatus, days: number]
  softDeleteAll: [status: ApplicationStatus]
}>()
const { t } = useI18n()
const router = useRouter()

const columns = computed<ColumnDef[]>(() => [
  {
    status: 'applied',
    label: t('candidates.status.applied'),
    color: 'text-blue-700',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    dotColor: 'bg-blue-500',
  },
  {
    status: 'prescanned',
    label: t('candidates.status.prescanned'),
    color: 'text-teal-700',
    bgColor: 'bg-teal-50',
    borderColor: 'border-teal-200',
    dotColor: 'bg-teal-500',
  },
  {
    status: 'interviewed',
    label: t('candidates.status.interviewed'),
    color: 'text-emerald-700',
    bgColor: 'bg-emerald-50',
    borderColor: 'border-emerald-200',
    dotColor: 'bg-emerald-500',
  },
  {
    status: 'shortlisted',
    label: t('candidates.status.shortlisted'),
    color: 'text-violet-700',
    bgColor: 'bg-violet-50',
    borderColor: 'border-violet-200',
    dotColor: 'bg-violet-500',
  },
  {
    status: 'hired',
    label: t('candidates.status.hired'),
    color: 'text-green-700',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    dotColor: 'bg-green-500',
  },
  {
    status: 'rejected',
    label: t('candidates.status.rejected'),
    color: 'text-red-700',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    dotColor: 'bg-red-500',
  },
  {
    status: 'archived',
    label: t('candidates.status.archived'),
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
    borderColor: 'border-gray-200',
    dotColor: 'bg-gray-400',
  },
])

const visibleColumns = computed(() =>
  props.interviewEnabled ? columns.value : columns.value.filter((c) => c.status !== 'interviewed'),
)

function getCandidates(status: ApplicationStatus): Application[] {
  return props.candidates.filter((c) => c.status === status)
}

const columnCounts = computed(() => {
  const c: Record<string, number> = {}
  for (const col of columns.value) c[col.status] = getCandidates(col.status).length
  return c
})

// Threshold dialog
const showThreshold = ref(false)
const thresholdVal = ref<number | null>(null)
const thresholdCtx = ref<{
  from: ApplicationStatus
  to: ApplicationStatus
  field: string
  dir: 'below' | 'above'
}>({ from: 'applied', to: 'rejected', field: 'match_score', dir: 'below' })

function openThresholdDialog(
  from: ApplicationStatus,
  to: ApplicationStatus,
  field: string,
  dir: 'below' | 'above',
) {
  thresholdCtx.value = { from, to, field, dir }
  thresholdVal.value = dir === 'below' ? 4 : 7
  showThreshold.value = true
}

function confirmThreshold() {
  if (thresholdVal.value == null) return
  const c = thresholdCtx.value
  emit('batchMoveByScore', c.from, c.to, c.field, thresholdVal.value, c.dir)
  showThreshold.value = false
}

function scoreFieldLabel(field: string): string {
  if (field === 'match_score') return t('candidates.scoreFields.cvMatch')
  if (field === 'prescanning_score') return t('candidates.scoreFields.prescan')
  return t('candidates.scoreFields.interview')
}

const thresholdTitle = computed(() => {
  const c = thresholdCtx.value
  return t('candidates.dialogs.thresholdTitle', {
    action:
      c.to === 'rejected' ? t('candidates.actions.reject') : t('candidates.actions.shortlist'),
    field: scoreFieldLabel(c.field),
    direction: t(`candidates.scoreDirections.${c.dir}`),
  })
})
const thresholdMax = computed(() => (thresholdCtx.value.field === 'match_score' ? 100 : 10))

// Days dialog
const showDays = ref(false)
const daysVal = ref<number | null>(7)
const daysCtx = ref<{ from: ApplicationStatus; to: ApplicationStatus }>({
  from: 'applied',
  to: 'rejected',
})

function openDaysDialog(from: ApplicationStatus, to: ApplicationStatus) {
  daysCtx.value = { from, to }
  daysVal.value = 7
  showDays.value = true
}

function confirmDays() {
  if (daysVal.value == null) return
  emit('batchMoveByDays', daysCtx.value.from, daysCtx.value.to, daysVal.value)
  showDays.value = false
}

function getMenuItems(status: ApplicationStatus) {
  return buildColumnMenuItems(status, {
    t,
    columnCounts: columnCounts.value,
    interviewEnabled: !!props.interviewEnabled,
    emitBatchMove: (f, t) => emit('batchMove', f, t),
    emitBatchMoveNoCv: (f, t) => emit('batchMoveNoCv', f, t),
    emitSoftDeleteAll: (s) => emit('softDeleteAll', s),
    openThresholdDialog,
    openDaysDialog,
  })
}

function viewCandidate(c: Application): void {
  router.push({ name: ROUTE_NAMES.CANDIDATE_DETAIL, params: { id: c.id } })
}

function onDrop(event: DragEvent, status: ApplicationStatus): void {
  const id = event.dataTransfer?.getData('candidateId')
  if (id) emit('statusChange', id, status)
}
</script>

<template>
  <div v-if="loading" class="flex items-center justify-center py-20">
    <i class="pi pi-spinner pi-spin text-3xl text-gray-300"></i>
  </div>

  <div v-else class="flex gap-3 overflow-x-auto pb-4 sm:gap-4">
    <KanbanColumn
      v-for="col in visibleColumns"
      :key="col.status"
      :column="col"
      :candidates="getCandidates(col.status)"
      :menu-items="getMenuItems(col.status)"
      @drop="onDrop($event, col.status)"
      @dragover="() => {}"
      @view-candidate="viewCandidate"
      @drag-start="() => {}"
    />
  </div>

  <Dialog
    v-model:visible="showThreshold"
    :header="thresholdTitle"
    modal
    :style="{ width: '360px' }"
  >
    <div class="flex flex-col gap-3">
      <label class="text-sm text-gray-600">{{
        thresholdCtx.dir === 'below'
          ? t('candidates.dialogs.scoreBelow')
          : t('candidates.dialogs.scoreAbove')
      }}</label>
      <InputNumber
        v-model="thresholdVal"
        :min="0"
        :max="thresholdMax"
        show-buttons
        class="w-full"
      />
    </div>
    <template #footer>
      <Button
        :label="t('common.cancel')"
        severity="secondary"
        text
        @click="showThreshold = false"
      />
      <Button :label="t('common.confirm')" @click="confirmThreshold" />
    </template>
  </Dialog>

  <Dialog
    v-model:visible="showDays"
    :header="t('candidates.dialogs.rejectIdleHeader')"
    modal
    :style="{ width: '360px' }"
  >
    <div class="flex flex-col gap-3">
      <label class="text-sm text-gray-600">{{ t('candidates.dialogs.appliedMoreThanDays') }}</label>
      <InputNumber
        v-model="daysVal"
        :min="1"
        :max="365"
        show-buttons
        :suffix="` ${t('candidates.dialogs.daysSuffix')}`"
        class="w-full"
      />
    </div>
    <template #footer>
      <Button :label="t('common.cancel')" severity="secondary" text @click="showDays = false" />
      <Button :label="t('common.confirm')" severity="danger" @click="confirmDays" />
    </template>
  </Dialog>
</template>
