<script setup lang="ts">
import { computed } from 'vue'

interface MatchDetails {
  overall?: number
  criteria_scores?: Record<string, number>
  notes?: string
  matching_skills?: string[]
  missing_skills?: string[]
}

const props = defineProps<{
  overallScore: number | null
  matchDetails: MatchDetails | null
  interviewScore: number | null
}>()

const cvScore = computed(() => props.overallScore)
const interviewScoreNorm = computed(() => {
  if (props.interviewScore === null) return null
  return Math.round(props.interviewScore * 10) // convert 1-10 to 0-100
})

const combinedScore = computed(() => {
  if (cvScore.value !== null && interviewScoreNorm.value !== null) {
    // 40% CV, 60% interview
    return Math.round(cvScore.value * 0.4 + interviewScoreNorm.value * 0.6)
  }
  if (interviewScoreNorm.value !== null) return interviewScoreNorm.value
  if (cvScore.value !== null) return cvScore.value
  return null
})

const recommendation = computed(() => {
  if (combinedScore.value === null) return null
  if (combinedScore.value >= 75) return { label: 'Strong Candidate — Recommend to move forward', color: 'bg-green-100 text-green-800 border-green-200', icon: 'pi-check-circle text-green-600' }
  if (combinedScore.value >= 55) return { label: 'Moderate Candidate — Consider for next round', color: 'bg-yellow-100 text-yellow-800 border-yellow-200', icon: 'pi-exclamation-circle text-yellow-600' }
  return { label: 'Weak Candidate — Not recommended to proceed', color: 'bg-red-100 text-red-800 border-red-200', icon: 'pi-times-circle text-red-600' }
})

function scoreBg(score: number): string {
  if (score >= 75) return 'bg-green-500'
  if (score >= 55) return 'bg-yellow-500'
  return 'bg-red-500'
}

function scoreTextColor(score: number): string {
  if (score >= 75) return 'text-green-600'
  if (score >= 55) return 'text-yellow-600'
  return 'text-red-600'
}
</script>

<template>
  <div v-if="combinedScore === null && cvScore === null && interviewScoreNorm === null" class="py-8 text-center text-sm text-gray-400">
    Analysis will be available after CV processing and interview completion.
  </div>

  <div v-else class="space-y-6">
    <!-- Recommendation Banner -->
    <div v-if="recommendation" class="rounded-xl border p-5" :class="recommendation.color">
      <div class="flex items-center gap-3">
        <i class="pi text-2xl" :class="recommendation.icon"></i>
        <div>
          <p class="font-semibold">{{ recommendation.label }}</p>
          <p v-if="combinedScore !== null" class="mt-0.5 text-sm opacity-75">
            Combined score: {{ combinedScore }}% (CV {{ cvScore ?? '—' }}% · Interview {{ interviewScoreNorm ?? '—' }}%)
          </p>
        </div>
      </div>
    </div>

    <!-- Score Comparison -->
    <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
      <!-- CV Match -->
      <div class="rounded-xl border border-gray-200 bg-white p-5 text-center">
        <p class="mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">CV Match</p>
        <div v-if="cvScore !== null">
          <p class="text-3xl font-bold" :class="scoreTextColor(cvScore)">{{ cvScore }}%</p>
          <p class="mt-1 text-xs text-gray-400">Based on resume analysis</p>
        </div>
        <p v-else class="text-2xl text-gray-300">—</p>
      </div>

      <!-- Interview Score -->
      <div class="rounded-xl border border-gray-200 bg-white p-5 text-center">
        <p class="mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">Interview</p>
        <div v-if="props.interviewScore !== null">
          <p class="text-3xl font-bold" :class="scoreTextColor(interviewScoreNorm!)">{{ props.interviewScore }}/10</p>
          <p class="mt-1 text-xs text-gray-400">AI pre-screening result</p>
        </div>
        <p v-else class="text-2xl text-gray-300">—</p>
      </div>

      <!-- Combined -->
      <div class="rounded-xl border-2 bg-white p-5 text-center" :class="combinedScore !== null ? 'border-blue-200' : 'border-gray-200'">
        <p class="mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">Overall</p>
        <div v-if="combinedScore !== null">
          <p class="text-3xl font-bold" :class="scoreTextColor(combinedScore)">{{ combinedScore }}%</p>
          <p class="mt-1 text-xs text-gray-400">40% CV · 60% Interview</p>
        </div>
        <p v-else class="text-2xl text-gray-300">—</p>
      </div>
    </div>

    <!-- Score Bar -->
    <div v-if="combinedScore !== null" class="rounded-lg border border-gray-200 bg-white p-4">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-gray-700">Combined Assessment</span>
        <span class="text-sm font-bold" :class="scoreTextColor(combinedScore)">{{ combinedScore }}%</span>
      </div>
      <div class="h-3 w-full rounded-full bg-gray-200">
        <div
          class="h-3 rounded-full transition-all"
          :class="scoreBg(combinedScore)"
          :style="{ width: `${combinedScore}%` }"
        ></div>
      </div>
      <div class="mt-1 flex justify-between text-[10px] text-gray-400">
        <span>0%</span>
        <span>Not Recommended</span>
        <span>|</span>
        <span>Consider</span>
        <span>|</span>
        <span>Recommended</span>
        <span>100%</span>
      </div>
    </div>
  </div>
</template>
