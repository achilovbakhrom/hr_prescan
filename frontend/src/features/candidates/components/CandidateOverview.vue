<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ApplicationStatusBadge from './ApplicationStatusBadge.vue'
import type {
  ApplicationDetail,
} from '../types/candidate.types'

const { t } = useI18n()

const props = defineProps<{
  candidate: ApplicationDetail
  loading: boolean
  prescanningScore?: number | null
  interviewScore?: number | null
  aiSummary?: string | null
}>()

const overallScore = computed(() => {
  const cv = props.candidate.matchScore
  const ps = props.prescanningScore != null ? Math.round(props.prescanningScore * 10) : null
  const iv = props.interviewScore != null ? Math.round(props.interviewScore * 10) : null

  // If all three available: 30% CV, 30% prescanning, 40% interview
  if (cv != null && ps != null && iv != null) return Math.round(cv * 0.3 + ps * 0.3 + iv * 0.4)
  // CV + prescanning: 40% CV, 60% prescanning
  if (cv != null && ps != null) return Math.round(cv * 0.4 + ps * 0.6)
  // CV + interview: 40% CV, 60% interview
  if (cv != null && iv != null) return Math.round(cv * 0.4 + iv * 0.6)
  // Prescanning + interview: 40% prescanning, 60% interview
  if (ps != null && iv != null) return Math.round(ps * 0.4 + iv * 0.6)
  // Single scores
  if (iv != null) return iv
  if (ps != null) return ps
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
        <p class="text-sm text-gray-500">{{ t('candidates.application.name') }}</p>
        <p class="font-medium">{{ props.candidate.candidateName }}</p>
      </div>
      <div>
        <p class="text-sm text-gray-500">{{ t('candidates.application.email') }}</p>
        <p class="font-medium">{{ props.candidate.candidateEmail }}</p>
      </div>
      <div>
        <p class="text-sm text-gray-500">{{ t('candidates.application.phone') }}</p>
        <p class="font-medium">
          {{ props.candidate.candidatePhone || 'Not provided' }}
        </p>
      </div>
      <div>
        <p class="text-sm text-gray-500">{{ t('nav.vacancies') }}</p>
        <p class="font-medium">{{ props.candidate.vacancyTitle }}</p>
      </div>
      <div>
        <p class="text-sm text-gray-500">{{ t('common.createdAt') }}</p>
        <p class="font-medium">
          {{ new Date(props.candidate.createdAt).toLocaleDateString() }}
        </p>
      </div>
    </div>

    <!-- CV Processing indicator -->
    <div
      v-if="props.candidate.cvFile && props.candidate.matchScore === null"
      class="flex items-center gap-3 rounded-lg border border-blue-200 bg-blue-50 p-3"
    >
      <i class="pi pi-spinner pi-spin text-blue-500"></i>
      <div>
        <p class="text-sm font-medium text-blue-800">CV is being analyzed...</p>
        <p class="text-xs text-blue-600">Extracting skills, experience, and calculating match score. This takes about 20 seconds.</p>
      </div>
    </div>

    <!-- Scores -->
    <div class="grid grid-cols-2 gap-2 sm:grid-cols-4 sm:gap-3">
      <div class="rounded-lg border border-gray-200 bg-gray-50 p-2 text-center sm:p-3">
        <p class="text-[9px] font-semibold text-gray-400 uppercase tracking-wide sm:text-[10px]">{{ t('candidates.matchScore') }}</p>
        <p v-if="props.candidate.matchScore !== null" class="mt-0.5 text-base font-bold sm:mt-1 sm:text-lg" :class="scoreColor(props.candidate.matchScore)">
          {{ props.candidate.matchScore }}%
        </p>
        <div v-else-if="props.candidate.cvFile" class="mt-1">
          <i class="pi pi-spinner pi-spin text-sm text-blue-400"></i>
        </div>
        <p v-else class="mt-0.5 text-base text-gray-300 sm:mt-1 sm:text-lg">—</p>
      </div>
      <div class="rounded-lg border border-gray-200 bg-gray-50 p-2 text-center sm:p-3">
        <p class="text-[9px] font-semibold text-gray-400 uppercase tracking-wide sm:text-[10px]">{{ t('candidates.prescanning') }}</p>
        <p v-if="props.prescanningScore != null" class="mt-0.5 text-base font-bold sm:mt-1 sm:text-lg" :class="scoreColor(props.prescanningScore * 10)">
          {{ props.prescanningScore }}/10
        </p>
        <p v-else class="mt-0.5 text-base text-gray-300 sm:mt-1 sm:text-lg">—</p>
      </div>
      <div class="rounded-lg border border-gray-200 bg-gray-50 p-2 text-center sm:p-3">
        <p class="text-[9px] font-semibold text-gray-400 uppercase tracking-wide sm:text-[10px]">{{ t('candidates.interview') }}</p>
        <p v-if="props.interviewScore != null" class="mt-0.5 text-base font-bold sm:mt-1 sm:text-lg" :class="scoreColor(props.interviewScore * 10)">
          {{ props.interviewScore }}/10
        </p>
        <p v-else class="mt-0.5 text-base text-gray-300 sm:mt-1 sm:text-lg">—</p>
      </div>
      <div class="rounded-lg border-2 p-2 text-center sm:p-3" :class="overallScore !== null ? 'border-blue-200 bg-blue-50' : 'border-gray-200 bg-gray-50'">
        <p class="text-[9px] font-semibold text-gray-400 uppercase tracking-wide sm:text-[10px]">{{ t('candidates.overallScore') }}</p>
        <p v-if="overallScore !== null" class="mt-0.5 text-base font-bold sm:mt-1 sm:text-lg" :class="scoreColor(overallScore)">
          {{ overallScore }}%
        </p>
        <p v-else class="mt-0.5 text-base text-gray-300 sm:mt-1 sm:text-lg">—</p>
        <p v-if="overallScore !== null" class="mt-0.5 hidden text-[10px] text-gray-400 sm:block">Combined score</p>
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
        <p class="mb-1 text-sm text-gray-500">{{ t('common.status') }}</p>
        <ApplicationStatusBadge :status="props.candidate.status" />
      </div>
    </div>
  </div>
</template>
