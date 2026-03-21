<script setup lang="ts">
import { computed } from 'vue'
import ApplicationStatusBadge from './ApplicationStatusBadge.vue'
import type {
  ApplicationDetail,
} from '../types/candidate.types'

const props = defineProps<{
  candidate: ApplicationDetail
  loading: boolean
  interviewScore?: number | null
  aiSummary?: string | null
}>()

const overallScore = computed(() => {
  const cv = props.candidate.matchScore
  const iv = props.interviewScore != null ? Math.round(props.interviewScore * 10) : null
  if (cv != null && iv != null) return Math.round(cv * 0.4 + iv * 0.6)
  if (iv != null) return iv
  if (cv != null) return cv
  return null
})

function scoreColor(score: number): string {
  if (score >= 75) return 'text-green-600'
  if (score >= 55) return 'text-yellow-600'
  return 'text-red-600'
}

function scoreBg(score: number): string {
  if (score >= 75) return 'bg-green-100 text-green-700'
  if (score >= 55) return 'bg-yellow-100 text-yellow-700'
  return 'bg-red-100 text-red-700'
}

const recommendation = computed(() => {
  if (overallScore.value === null) return null
  if (overallScore.value >= 75) return { label: 'Recommend to move forward', icon: 'pi-check-circle', cls: 'bg-green-50 border-green-200 text-green-800' }
  if (overallScore.value >= 55) return { label: 'Consider for next round', icon: 'pi-exclamation-circle', cls: 'bg-yellow-50 border-yellow-200 text-yellow-800' }
  return { label: 'Not recommended to proceed', icon: 'pi-times-circle', cls: 'bg-red-50 border-red-200 text-red-800' }
})

</script>

<template>
  <div class="space-y-4">
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <div>
        <p class="text-sm text-gray-500">Name</p>
        <p class="font-medium">{{ props.candidate.candidateName }}</p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Email</p>
        <p class="font-medium">{{ props.candidate.candidateEmail }}</p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Phone</p>
        <p class="font-medium">
          {{ props.candidate.candidatePhone || 'Not provided' }}
        </p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Vacancy</p>
        <p class="font-medium">{{ props.candidate.vacancyTitle }}</p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Applied</p>
        <p class="font-medium">
          {{ new Date(props.candidate.createdAt).toLocaleDateString() }}
        </p>
      </div>
    </div>

    <!-- Scores -->
    <div class="grid grid-cols-3 gap-3">
      <div class="rounded-lg border border-gray-200 bg-gray-50 p-3 text-center">
        <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">CV Match</p>
        <p v-if="props.candidate.matchScore !== null" class="mt-1 text-lg font-bold" :class="scoreColor(props.candidate.matchScore)">
          {{ props.candidate.matchScore }}%
        </p>
        <p v-else class="mt-1 text-lg text-gray-300">—</p>
      </div>
      <div class="rounded-lg border border-gray-200 bg-gray-50 p-3 text-center">
        <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Interview</p>
        <p v-if="props.interviewScore != null" class="mt-1 text-lg font-bold" :class="scoreColor(props.interviewScore * 10)">
          {{ props.interviewScore }}/10
        </p>
        <p v-else class="mt-1 text-lg text-gray-300">—</p>
      </div>
      <div class="rounded-lg border-2 p-3 text-center" :class="overallScore !== null ? 'border-blue-200 bg-blue-50' : 'border-gray-200 bg-gray-50'">
        <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Overall</p>
        <p v-if="overallScore !== null" class="mt-1 text-lg font-bold" :class="scoreColor(overallScore)">
          {{ overallScore }}%
        </p>
        <p v-else class="mt-1 text-lg text-gray-300">—</p>
        <p v-if="overallScore !== null" class="mt-0.5 text-[10px] text-gray-400">40% CV · 60% Interview</p>
      </div>
    </div>

    <!-- AI Decision & Reason -->
    <div v-if="recommendation" class="rounded-lg border p-4" :class="recommendation.cls">
      <div class="flex items-start gap-3">
        <i class="pi mt-0.5 text-lg" :class="recommendation.icon"></i>
        <div>
          <p class="font-semibold">{{ recommendation.label }}</p>
          <p v-if="props.aiSummary" class="mt-1 text-sm opacity-80">{{ props.aiSummary }}</p>
        </div>
      </div>
    </div>

    <div class="flex flex-wrap items-center gap-3">
      <div>
        <p class="mb-1 text-sm text-gray-500">Status</p>
        <ApplicationStatusBadge :status="props.candidate.status" />
      </div>
    </div>
  </div>
</template>
