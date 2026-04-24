<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import TranslatableText from '@/shared/components/TranslatableText.vue'
import { calculateOverallScore, normalizeScreeningScore } from '../utils/score'

const props = defineProps<{
  cvMatchScore: number | null
  matchDetails: MatchDetails | null
  matchNotesTranslations?: Record<string, string>
  applicationId?: string
  prescanningScore: number | null
  interviewScore: number | null
}>()

const { t } = useI18n()

interface MatchDetails {
  overall?: number
  criteria_scores?: Record<string, number>
  notes?: string
  matching_skills?: string[]
  missing_skills?: string[]
}

const cvScore = computed(() => props.cvMatchScore)
const prescanningScoreNorm = computed(() => normalizeScreeningScore(props.prescanningScore))
const interviewScoreNorm = computed(() => normalizeScreeningScore(props.interviewScore))
const combinedScore = computed(() =>
  calculateOverallScore({
    cvMatchScore: props.cvMatchScore,
    prescanningScore: props.prescanningScore,
    interviewScore: props.interviewScore,
  }),
)

const recommendation = computed(() => {
  if (combinedScore.value === null) return null
  if (combinedScore.value >= 75)
    return {
      label: t('candidates.recommendation.strong'),
      color: 'bg-green-100 text-green-800 border-green-200',
      icon: 'pi-check-circle text-green-600',
    }
  if (combinedScore.value >= 55)
    return {
      label: t('candidates.recommendation.moderate'),
      color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      icon: 'pi-exclamation-circle text-yellow-600',
    }
  return {
    label: t('candidates.recommendation.weak'),
    color: 'bg-red-100 text-red-800 border-red-200',
    icon: 'pi-times-circle text-red-600',
  }
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

const scoreBreakdownLabel = computed(() => {
  const parts: string[] = []
  if (cvScore.value !== null) parts.push(`${t('candidates.cv')} ${cvScore.value}%`)
  if (prescanningScoreNorm.value !== null)
    parts.push(`${t('candidates.prescanning')} ${prescanningScoreNorm.value}%`)
  if (interviewScoreNorm.value !== null)
    parts.push(`${t('candidates.interview')} ${interviewScoreNorm.value}%`)
  return parts.join(' · ')
})
</script>

<template>
  <div
    v-if="
      combinedScore === null &&
      cvScore === null &&
      prescanningScoreNorm === null &&
      interviewScoreNorm === null
    "
    class="py-8 text-center text-sm text-gray-400"
  >
    {{ t('candidates.matchScoreView.noAnalysis') }}
  </div>

  <div v-else class="space-y-6">
    <!-- Recommendation Banner -->
    <div v-if="recommendation" class="rounded-xl border p-5" :class="recommendation.color">
      <div class="flex items-center gap-3">
        <i class="pi text-2xl" :class="recommendation.icon"></i>
        <div>
          <p class="font-semibold">{{ recommendation.label }}</p>
          <p v-if="combinedScore !== null" class="mt-0.5 text-sm opacity-75">
            {{ t('candidates.overviewDetails.combinedScore') }}: {{ combinedScore }}% ({{
              scoreBreakdownLabel
            }})
          </p>
        </div>
      </div>
    </div>

    <!-- Score Comparison -->
    <div class="grid grid-cols-2 gap-2 sm:grid-cols-4 sm:gap-4">
      <!-- CV Match -->
      <div
        class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-3 text-center sm:p-5"
      >
        <p
          class="mb-1 text-[9px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide sm:mb-2 sm:text-xs"
        >
          {{ t('candidates.matchScore') }}
        </p>
        <div v-if="cvScore !== null">
          <p class="text-xl font-bold sm:text-3xl" :class="scoreTextColor(cvScore)">
            {{ cvScore }}%
          </p>
          <p class="mt-1 hidden text-xs text-gray-400 dark:text-gray-500 sm:block">
            {{ t('candidates.matchScoreView.basedOnResume') }}
          </p>
        </div>
        <p v-else class="text-xl text-gray-300 dark:text-gray-600 sm:text-2xl">—</p>
      </div>

      <!-- Prescanning Score -->
      <div
        class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-3 text-center sm:p-5"
      >
        <p
          class="mb-1 text-[9px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide sm:mb-2 sm:text-xs"
        >
          {{ t('candidates.prescanning') }}
        </p>
        <div v-if="props.prescanningScore !== null">
          <p class="text-xl font-bold sm:text-3xl" :class="scoreTextColor(prescanningScoreNorm!)">
            {{ props.prescanningScore }}/10
          </p>
          <p class="mt-1 hidden text-xs text-gray-400 dark:text-gray-500 sm:block">
            {{ t('candidates.matchScoreView.aiPrescanResult') }}
          </p>
        </div>
        <p v-else class="text-xl text-gray-300 dark:text-gray-600 sm:text-2xl">—</p>
      </div>

      <!-- Interview Score -->
      <div
        class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-3 text-center sm:p-5"
      >
        <p
          class="mb-1 text-[9px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide sm:mb-2 sm:text-xs"
        >
          {{ t('candidates.interview') }}
        </p>
        <div v-if="props.interviewScore !== null">
          <p class="text-xl font-bold sm:text-3xl" :class="scoreTextColor(interviewScoreNorm!)">
            {{ props.interviewScore }}/10
          </p>
          <p class="mt-1 hidden text-xs text-gray-400 dark:text-gray-500 sm:block">
            {{ t('candidates.matchScoreView.aiInterviewResult') }}
          </p>
        </div>
        <p v-else class="text-xl text-gray-300 dark:text-gray-600 sm:text-2xl">—</p>
      </div>

      <!-- Combined -->
      <div
        class="rounded-xl border-2 bg-white dark:bg-gray-800 p-3 text-center sm:p-5"
        :class="combinedScore !== null ? 'border-blue-200' : 'border-gray-200'"
      >
        <p
          class="mb-1 text-[9px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide sm:mb-2 sm:text-xs"
        >
          {{ t('candidates.overallScore') }}
        </p>
        <div v-if="combinedScore !== null">
          <p class="text-xl font-bold sm:text-3xl" :class="scoreTextColor(combinedScore)">
            {{ combinedScore }}%
          </p>
          <p class="mt-1 hidden text-xs text-gray-400 dark:text-gray-500 sm:block">
            {{ t('candidates.overviewDetails.combinedScore') }}
          </p>
        </div>
        <p v-else class="text-xl text-gray-300 dark:text-gray-600 sm:text-2xl">—</p>
      </div>
    </div>

    <!-- Score Bar -->
    <div
      v-if="combinedScore !== null"
      class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4"
    >
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-gray-700">{{
          t('candidates.matchScoreView.combinedAssessment')
        }}</span>
        <span class="text-sm font-bold" :class="scoreTextColor(combinedScore)"
          >{{ combinedScore }}%</span
        >
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
        <span>{{ t('candidates.matchScoreView.notRecommendedLabel') }}</span>
        <span>|</span>
        <span>{{ t('candidates.matchScoreView.considerLabel') }}</span>
        <span>|</span>
        <span>{{ t('candidates.matchScoreView.recommendedLabel') }}</span>
        <span>100%</span>
      </div>
    </div>

    <!-- AI Match Notes -->
    <div
      v-if="props.matchDetails?.notes"
      class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4"
    >
      <p
        class="mb-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide"
      >
        {{ t('candidates.matchScoreView.aiNotes') }}
      </p>
      <TranslatableText
        v-if="props.applicationId"
        :text="props.matchDetails.notes"
        :translations="props.matchNotesTranslations || {}"
        model="application"
        :object-id="props.applicationId"
        field="match_notes"
      >
        <template #default="{ text }">
          <p class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{{ text }}</p>
        </template>
      </TranslatableText>
      <p v-else class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
        {{ props.matchDetails.notes }}
      </p>
    </div>
  </div>
</template>
