<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ApplicationStatusBadge from './ApplicationStatusBadge.vue'
import TranslatableText from '@/shared/components/TranslatableText.vue'
import { calculateOverallScore, normalizeScreeningScore } from '../utils/score'
import type { ApplicationDetail } from '../types/candidate.types'

const props = defineProps<{
  candidate: ApplicationDetail
  loading: boolean
  prescanningScore?: number | null
  interviewScore?: number | null
  aiSummary?: string | null
  aiSummaryTranslations?: Record<string, string>
  aiSummaryInterviewId?: string
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

function scoreColor(score: number): string {
  if (score >= 75) return 'text-green-600'
  if (score >= 55) return 'text-yellow-600'
  return 'text-red-600'
}

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
      class="flex items-center gap-3 rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950 p-3"
    >
      <i class="pi pi-spinner pi-spin text-blue-500"></i>
      <div>
        <p class="text-sm font-medium text-blue-800">{{ t('candidates.cvData.analyzing') }}</p>
        <p class="text-xs text-blue-600">{{ t('candidates.cvData.analyzingHint') }}</p>
      </div>
    </div>

    <!-- Scores -->
    <div class="grid grid-cols-2 gap-2 sm:grid-cols-4 sm:gap-3">
      <div
        class="rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 p-2 text-center sm:p-3"
      >
        <p
          class="text-[9px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide sm:text-[10px]"
        >
          {{ t('candidates.matchScore') }}
        </p>
        <p
          v-if="props.candidate.matchScore !== null"
          class="mt-0.5 text-base font-bold sm:mt-1 sm:text-lg"
          :class="scoreColor(props.candidate.matchScore)"
        >
          {{ props.candidate.matchScore }}%
        </p>
        <div v-else-if="props.candidate.cvFile" class="mt-1">
          <i class="pi pi-spinner pi-spin text-sm text-blue-400"></i>
        </div>
        <p v-else class="mt-0.5 text-base text-gray-300 dark:text-gray-600 sm:mt-1 sm:text-lg">—</p>
      </div>
      <div
        class="rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 p-2 text-center sm:p-3"
      >
        <p
          class="text-[9px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide sm:text-[10px]"
        >
          {{ t('candidates.prescanning') }}
        </p>
        <p
          v-if="props.prescanningScore != null"
          class="mt-0.5 text-base font-bold sm:mt-1 sm:text-lg"
          :class="scoreColor(normalizeScreeningScore(props.prescanningScore) ?? 0)"
        >
          {{ props.prescanningScore }}/10
        </p>
        <p v-else class="mt-0.5 text-base text-gray-300 dark:text-gray-600 sm:mt-1 sm:text-lg">—</p>
      </div>
      <div
        class="rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 p-2 text-center sm:p-3"
      >
        <p
          class="text-[9px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide sm:text-[10px]"
        >
          {{ t('candidates.interview') }}
        </p>
        <p
          v-if="props.interviewScore != null"
          class="mt-0.5 text-base font-bold sm:mt-1 sm:text-lg"
          :class="scoreColor(normalizeScreeningScore(props.interviewScore) ?? 0)"
        >
          {{ props.interviewScore }}/10
        </p>
        <p v-else class="mt-0.5 text-base text-gray-300 dark:text-gray-600 sm:mt-1 sm:text-lg">—</p>
      </div>
      <div
        class="rounded-lg border-2 p-2 text-center sm:p-3"
        :class="overallScore !== null ? 'border-blue-200 bg-blue-50' : 'border-gray-200 bg-gray-50'"
      >
        <p
          class="text-[9px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide sm:text-[10px]"
        >
          {{ t('candidates.overallScore') }}
        </p>
        <p
          v-if="overallScore !== null"
          class="mt-0.5 text-base font-bold sm:mt-1 sm:text-lg"
          :class="scoreColor(overallScore)"
        >
          {{ overallScore }}%
        </p>
        <p v-else class="mt-0.5 text-base text-gray-300 dark:text-gray-600 sm:mt-1 sm:text-lg">—</p>
        <p
          v-if="overallScore !== null"
          class="mt-0.5 hidden text-[10px] text-gray-400 dark:text-gray-500 sm:block"
        >
          {{ t('candidates.overviewDetails.combinedScore') }}
        </p>
      </div>
    </div>

    <!-- AI Decision & Reason -->
    <div v-if="recommendation" class="rounded-lg border p-4" :class="recommendation.cls">
      <div class="flex items-start gap-3">
        <i class="pi mt-0.5 text-lg" :class="recommendation.icon"></i>
        <div>
          <p class="font-semibold">{{ recommendation.label }}</p>
          <TranslatableText
            v-if="props.aiSummary && props.aiSummaryInterviewId"
            :text="props.aiSummary"
            :translations="props.aiSummaryTranslations || {}"
            model="interview"
            :object-id="props.aiSummaryInterviewId"
            field="ai_summary"
            @translated="(tr) => emit('update:aiSummaryTranslations', tr)"
          >
            <template #default="{ text }">
              <p class="mt-1 text-sm opacity-80">{{ text }}</p>
            </template>
          </TranslatableText>
          <p v-else-if="props.aiSummary" class="mt-1 text-sm opacity-80">{{ props.aiSummary }}</p>
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
