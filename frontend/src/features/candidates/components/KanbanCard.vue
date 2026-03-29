<script setup lang="ts">
import type { Application } from '../types/candidate.types'
import type { ColumnDef } from './KanbanColumn.vue'

const props = defineProps<{
  candidate: Application
  column: ColumnDef
}>()

const emit = defineEmits<{
  click: []
  dragStart: [event: DragEvent]
}>()

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

function onDragStart(event: DragEvent): void {
  event.dataTransfer?.setData('candidateId', props.candidate.id)
  emit('dragStart', event)
}
</script>

<template>
  <div
    draggable="true"
    class="cursor-pointer rounded-lg border border-gray-100 bg-white p-3 shadow-sm transition-all hover:shadow-md"
    @click="emit('click')"
    @dragstart="onDragStart"
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
</template>
