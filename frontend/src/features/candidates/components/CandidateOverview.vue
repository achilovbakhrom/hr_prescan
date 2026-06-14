<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ApplicationStatusBadge from './ApplicationStatusBadge.vue'
import CandidateScreeningLinks from './CandidateScreeningLinks.vue'
import CandidateOverviewDecision from './CandidateOverviewDecision.vue'
import CandidateOverviewScores from './CandidateOverviewScores.vue'
import { calculateOverallScore } from '../utils/score'
import type { ApplicationDetail } from '../types/candidate.types'
import type { CandidateAnalysisSession } from '../composables/useInterviewData'

const props = defineProps<{
  candidate: ApplicationDetail
  loading: boolean
  prescanningScore?: number | null
  interviewScore?: number | null
  aiSummary?: string | null
  aiSummaryTranslations?: Record<string, string>
  aiSummaryInterviewId?: string
  analysisSessions: CandidateAnalysisSession[]
}>()

const emit = defineEmits<{
  'update:aiSummaryTranslations': [tr: Record<string, string>]
}>()

const { t } = useI18n()

const overallScore = computed(() =>
  calculateOverallScore({
    cvMatchScore: props.candidate.matchScore,
    prescanningScore: props.prescanningScore,
    interviewScore: props.interviewScore,
  }),
)

const recommendation = computed(() => {
  if (overallScore.value === null) return null
  if (overallScore.value >= 75)
    return {
      label: t('candidates.recommendation.moveForward'),
      icon: 'pi-check-circle',
      cls: 'bg-green-50 border-green-200 text-green-800',
    }
  if (overallScore.value >= 55)
    return {
      label: t('candidates.recommendation.consider'),
      icon: 'pi-exclamation-circle',
      cls: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    }
  return {
    label: t('candidates.recommendation.notRecommended'),
    icon: 'pi-times-circle',
    cls: 'bg-red-50 border-red-200 text-red-800',
  }
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
          {{ props.candidate.candidatePhone || t('candidates.overviewDetails.notProvided') }}
        </p>
      </div>
      <div v-if="props.candidate.linkedinUrl">
        <p class="text-sm text-gray-500">{{ t('candidates.application.linkedin') }}</p>
        <a
          :href="props.candidate.linkedinUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex max-w-full items-center gap-1.5 font-medium text-[color:var(--color-accent)] hover:underline"
        >
          <i class="pi pi-linkedin shrink-0"></i>
          <span class="truncate">{{ props.candidate.linkedinUrl }}</span>
          <i class="pi pi-external-link shrink-0 text-xs"></i>
        </a>
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

    <CandidateScreeningLinks
      :prescan-token="props.candidate.prescanToken"
      :interview-token="props.candidate.interviewToken"
      :interview-enabled="props.candidate.interviewEnabled"
    />

    <div
      v-if="props.candidate.cvFile && props.candidate.matchScore === null"
      class="flex items-center gap-3 rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950 p-3"
    >
      <i class="pi pi-spinner pi-spin text-blue-500"></i>
      <div>
        <p class="text-sm font-medium text-blue-800">{{ t('candidates.cvData.analyzing') }}</p>
        <p class="text-xs text-blue-600">{{ t('candidates.cvData.analyzingHint') }}</p>
      </div>
    </div>

    <CandidateOverviewScores
      :match-score="props.candidate.matchScore"
      :has-cv="Boolean(props.candidate.cvFile)"
      :prescanning-score="props.prescanningScore"
      :interview-score="props.interviewScore"
      :overall-score="overallScore"
    />

    <CandidateOverviewDecision
      :recommendation="recommendation"
      :ai-summary="props.aiSummary"
      :ai-summary-translations="props.aiSummaryTranslations"
      :ai-summary-interview-id="props.aiSummaryInterviewId"
      :analysis-sessions="props.analysisSessions"
      @update:ai-summary-translations="emit('update:aiSummaryTranslations', $event)"
    />

    <div class="flex flex-wrap items-center gap-3">
      <div>
        <p class="mb-1 text-sm text-gray-500">{{ t('common.status') }}</p>
        <ApplicationStatusBadge :status="props.candidate.status" />
      </div>
    </div>
  </div>
</template>
