<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ProgressBar from 'primevue/progressbar'
import TranslatableText from '@/shared/components/TranslatableText.vue'
import { getLocale } from '@/shared/i18n'
import type { DecisionSupport } from '@/shared/types/interview.types'
import InterviewSummarySections from './InterviewSummarySections.vue'
import { buildEvidenceQuery } from '../utils/interviewEvidence'

defineProps<{
  overallScore: number | null
  aiSummary: string
  aiSummaryTranslations: Record<string, string>
  decisionSupport?: DecisionSupport
  interviewId: string
  scores: InterviewScore[]
}>()

const emit = defineEmits<{
  'update:aiSummaryTranslations': [tr: Record<string, string>]
  findEvidence: [query: string]
}>()

const { t } = useI18n()

interface InterviewScore {
  id: string
  criteria: string
  criteriaName: string
  criteriaTranslations?: Record<string, string>
  score: number
  aiNotes: string
  aiNotesTranslations: Record<string, string>
  evidence?: Array<{
    quote: string
    timestamp?: number | null
    speaker?: string
    line?: number | null
  }>
}

const currentLocale = computed(() => getLocale())

function getLocalizedCriteriaName(score: InterviewScore): string {
  // Translations are stored as "Name: Description" — split on first ": "
  const translated = score.criteriaTranslations?.[currentLocale.value]
  if (!translated) return score.criteriaName
  return translated.split(': ')[0] || score.criteriaName
}

function scoreColor(score: number): string {
  if (score >= 8) return 'text-green-600'
  if (score >= 6) return 'text-blue-600'
  if (score >= 4) return 'text-yellow-600'
  return 'text-red-600'
}

function scoreBg(score: number): string {
  if (score >= 8) return 'bg-green-500'
  if (score >= 6) return 'bg-blue-500'
  if (score >= 4) return 'bg-yellow-500'
  return 'bg-red-500'
}

function handleFindEvidence(score: InterviewScore): void {
  const query =
    score.evidence?.find((item) => item.quote)?.quote ||
    buildEvidenceQuery({
      criteriaName: getLocalizedCriteriaName(score),
      aiNotes: score.aiNotes,
    })
  if (query) emit('findEvidence', query)
}
</script>

<template>
  <div>
    <div
      v-if="overallScore !== null"
      class="mb-4 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 p-5"
    >
      <div class="flex items-center justify-between">
        <div>
          <p class="text-xs font-medium uppercase tracking-wide text-blue-600">
            {{ t('interviews.overallScore') }}
          </p>
          <p class="mt-1 text-4xl font-bold" :class="scoreColor(overallScore)">
            {{ overallScore }}<span class="text-lg text-gray-400">/10</span>
          </p>
        </div>
        <div
          class="flex h-16 w-16 items-center justify-center rounded-full border-4"
          :class="scoreBg(overallScore) + ' border-opacity-20'"
        >
          <span class="text-xl font-bold text-white">{{ Math.round(overallScore) }}</span>
        </div>
      </div>
    </div>

    <InterviewSummarySections
      v-if="scores?.length"
      :overall-score="overallScore"
      :scores="scores"
      :decision-support="decisionSupport"
    />

    <div
      v-if="aiSummary"
      class="mb-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 p-4"
    >
      <p class="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500">
        {{ t('interviews.aiAssessment') }}
      </p>
      <TranslatableText
        :text="aiSummary"
        :translations="aiSummaryTranslations || {}"
        model="interview"
        :object-id="interviewId"
        field="ai_summary"
        @translated="(tr) => emit('update:aiSummaryTranslations', tr)"
      >
        <template #default="{ text }"
          ><p class="text-sm leading-relaxed text-gray-700">{{ text }}</p></template
        >
      </TranslatableText>
    </div>

    <div v-if="scores?.length" class="space-y-3">
      <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">
        {{ t('interviews.criteriaBreakdown') }}
      </p>
      <div
        v-for="score in scores"
        :key="score.id"
        class="rounded-lg border border-gray-200 dark:border-gray-700 p-3"
      >
        <div class="mb-1.5 flex items-center justify-between gap-3">
          <span class="text-sm font-medium text-gray-700">{{
            getLocalizedCriteriaName(score)
          }}</span>
          <div class="flex shrink-0 items-center gap-2">
            <button
              class="rounded-md px-2 py-1 text-xs font-medium text-blue-600 transition-colors hover:bg-blue-50"
              type="button"
              @click="handleFindEvidence(score)"
            >
              <i class="pi pi-search mr-1"></i>
              {{ t('interviews.findEvidence', 'Evidence') }}
            </button>
            <span class="text-sm font-bold" :class="scoreColor(score.score)"
              >{{ score.score }}/10</span
            >
          </div>
        </div>
        <ProgressBar :value="score.score * 10" :show-value="false" style="height: 6px" />
        <TranslatableText
          v-if="score.aiNotes"
          :text="score.aiNotes"
          :translations="score.aiNotesTranslations || {}"
          model="interview_score"
          :object-id="score.id"
          field="ai_notes"
          @translated="(tr) => (score.aiNotesTranslations = tr)"
        >
          <template #default="{ text }"
            ><p class="mt-1.5 text-xs text-gray-500">{{ text }}</p></template
          >
        </TranslatableText>
        <div v-if="score.evidence?.length" class="mt-3 space-y-1.5">
          <button
            v-for="item in score.evidence"
            :key="`${item.line ?? item.quote}-${item.timestamp ?? ''}`"
            class="block w-full rounded-md bg-blue-50 px-2.5 py-2 text-left text-xs text-blue-900 transition-colors hover:bg-blue-100"
            type="button"
            @click="emit('findEvidence', item.quote)"
          >
            <span class="font-semibold">{{ t('interviews.evidence', 'Evidence') }}:</span>
            {{ item.quote }}
          </button>
        </div>
      </div>
    </div>

    <p v-else class="py-4 text-center text-sm text-gray-400">{{ t('interviews.noScores') }}</p>
  </div>
</template>
