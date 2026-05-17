<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { DecisionSupport } from '@/shared/types/interview.types'

interface InterviewScore {
  id: string
  criteriaName: string
  score: number
  aiNotes?: string
}

const props = defineProps<{
  overallScore: number | null
  scores: InterviewScore[]
  decisionSupport?: DecisionSupport
}>()

const { t } = useI18n()

const strengths = computed(() => props.decisionSupport?.strengths?.slice(0, 3) || [])
const risks = computed(() => props.decisionSupport?.risks?.slice(0, 3) || [])
const fallbackStrengths = computed(() =>
  props.scores.filter((score) => score.score >= 8).slice(0, 3),
)
const fallbackRisks = computed(() => props.scores.filter((score) => score.score <= 5).slice(0, 3))
const recommendation = computed(() => {
  if (props.decisionSupport?.recommendation) return props.decisionSupport.recommendation
  if (props.overallScore === null) return t('interviews.recommendationManual', 'Review manually')
  if (props.overallScore >= 7.5) {
    return t('interviews.recommendationAdvance', 'Recommended for next step')
  }
  if (props.overallScore >= 5.5) return t('interviews.recommendationReview', 'Needs HR review')
  return t('interviews.recommendationRisk', 'High risk / do not advance without review')
})
const nextStep = computed(
  () => props.decisionSupport?.nextStep || props.decisionSupport?.next_step || '',
)
</script>

<template>
  <div class="mb-4 grid gap-3 md:grid-cols-4">
    <div class="rounded-lg border border-gray-200 dark:border-gray-700 p-3">
      <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
        {{ t('interviews.recommendation', 'Recommendation') }}
      </p>
      <p class="text-sm font-medium text-gray-800">{{ recommendation }}</p>
    </div>
    <div class="rounded-lg border border-gray-200 dark:border-gray-700 p-3">
      <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
        {{ t('interviews.strengths', 'Strengths') }}
      </p>
      <p v-if="!strengths.length && !fallbackStrengths.length" class="text-sm text-gray-500">
        {{ t('interviews.noClearStrengths', 'No clear strengths yet.') }}
      </p>
      <ul v-else-if="strengths.length" class="space-y-1 text-sm text-gray-700">
        <li v-for="strength in strengths" :key="strength">{{ strength }}</li>
      </ul>
      <ul v-else class="space-y-1 text-sm text-gray-700">
        <li v-for="score in fallbackStrengths" :key="score.id">
          {{ score.criteriaName }}: {{ score.score }}/10
        </li>
      </ul>
    </div>
    <div class="rounded-lg border border-gray-200 dark:border-gray-700 p-3">
      <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
        {{ t('interviews.risks', 'Risks') }}
      </p>
      <p v-if="!risks.length && !fallbackRisks.length" class="text-sm text-gray-500">
        {{ t('interviews.noMajorRisks', 'No major risks flagged.') }}
      </p>
      <ul v-else-if="risks.length" class="space-y-1 text-sm text-gray-700">
        <li v-for="risk in risks" :key="risk">{{ risk }}</li>
      </ul>
      <ul v-else class="space-y-1 text-sm text-gray-700">
        <li v-for="score in fallbackRisks" :key="score.id">
          {{ score.criteriaName }}: {{ score.score }}/10
        </li>
      </ul>
    </div>
    <div class="rounded-lg border border-gray-200 dark:border-gray-700 p-3">
      <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
        {{ t('interviews.nextStep', 'Next step') }}
      </p>
      <p class="text-sm text-gray-700">
        {{ nextStep || t('interviews.nextStepDefault', 'Review evidence before deciding.') }}
      </p>
    </div>
  </div>
</template>
