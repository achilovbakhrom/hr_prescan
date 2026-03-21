<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Application, ApplicationStatus } from '../types/candidate.types'

const props = defineProps<{
  candidates: Application[]
  loading: boolean
}>()

const emit = defineEmits<{
  statusChange: [id: string, status: ApplicationStatus]
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
  { status: 'interview_in_progress', label: 'Interview', color: 'text-amber-700', bgColor: 'bg-amber-50', borderColor: 'border-amber-200', dotColor: 'bg-amber-500' },
  { status: 'interview_completed', label: 'Completed', color: 'text-emerald-700', bgColor: 'bg-emerald-50', borderColor: 'border-emerald-200', dotColor: 'bg-emerald-500' },
  { status: 'shortlisted', label: 'Shortlisted', color: 'text-violet-700', bgColor: 'bg-violet-50', borderColor: 'border-violet-200', dotColor: 'bg-violet-500' },
  { status: 'rejected', label: 'Rejected', color: 'text-red-700', bgColor: 'bg-red-50', borderColor: 'border-red-200', dotColor: 'bg-red-500' },
  { status: 'expired', label: 'Expired', color: 'text-gray-700', bgColor: 'bg-gray-50', borderColor: 'border-gray-200', dotColor: 'bg-gray-500' },
]

function getCandidatesForColumn(status: ApplicationStatus): Application[] {
  // Group some statuses together
  if (status === 'interview_completed') {
    return props.candidates.filter((c) =>
      c.status === 'interview_completed' || c.status === 'reviewing',
    )
  }
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

  <div v-else class="flex gap-4 overflow-x-auto pb-4">
    <div
      v-for="column in columns"
      :key="column.status"
      class="flex w-64 shrink-0 flex-col rounded-xl border border-gray-100 bg-gray-50/50"
      @drop="onDrop($event, column.status)"
      @dragover="onDragOver"
    >
      <!-- Column header -->
      <div class="flex items-center justify-between px-4 py-3">
        <div class="flex items-center gap-2">
          <div class="h-2 w-2 rounded-full" :class="column.dotColor"></div>
          <span class="text-sm font-semibold text-gray-700">{{ column.label }}</span>
        </div>
        <span
          class="flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-xs font-medium"
          :class="[column.bgColor, column.color]"
        >
          {{ columnCounts[column.status] }}
        </span>
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
          </div>

          <div class="mt-2.5 flex items-center justify-between">
            <span class="text-xs text-gray-400">{{ formatDate(candidate.createdAt) }}</span>
            <div class="flex items-center gap-1.5">
              <span
                v-if="candidate.interviewScore !== null && candidate.interviewScore !== undefined"
                class="rounded-md px-1.5 py-0.5 text-xs font-medium"
                :class="
                  candidate.interviewScore >= 7
                    ? 'bg-emerald-50 text-emerald-700'
                    : candidate.interviewScore >= 5
                      ? 'bg-amber-50 text-amber-700'
                      : 'bg-red-50 text-red-700'
                "
                :title="'Interview score'"
              >
                <i class="pi pi-star-fill mr-0.5" style="font-size: 8px"></i>{{ candidate.interviewScore }}/10
              </span>
              <span
                v-if="candidate.matchScore !== null"
                class="rounded-md px-1.5 py-0.5 text-xs font-medium bg-blue-50 text-blue-700"
                :title="'CV match score'"
              >
                {{ candidate.matchScore }}%
              </span>
              <span v-if="candidate.matchScore === null && (candidate.interviewScore === null || candidate.interviewScore === undefined)" class="text-xs text-gray-400">No score</span>
            </div>
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
</template>
