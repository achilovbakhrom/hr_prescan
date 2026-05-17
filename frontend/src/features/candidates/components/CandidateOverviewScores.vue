<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { normalizeScreeningScore } from '../utils/score'

defineProps<{
  matchScore: number | null
  hasCv: boolean
  prescanningScore?: number | null
  interviewScore?: number | null
  overallScore: number | null
}>()

const { t } = useI18n()

function scoreColor(score: number): string {
  if (score >= 75) return 'text-green-600'
  if (score >= 55) return 'text-yellow-600'
  return 'text-red-600'
}
</script>

<template>
  <div class="grid grid-cols-2 gap-2 sm:grid-cols-4 sm:gap-3">
    <div
      class="rounded-lg border border-gray-200 bg-gray-50 p-2 text-center dark:border-gray-700 dark:bg-gray-900 sm:p-3"
    >
      <p
        class="text-[9px] font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500 sm:text-[10px]"
      >
        {{ t('candidates.matchScore') }}
      </p>
      <p
        v-if="matchScore !== null"
        class="mt-0.5 text-base font-bold sm:mt-1 sm:text-lg"
        :class="scoreColor(matchScore)"
      >
        {{ matchScore }}%
      </p>
      <div v-else-if="hasCv" class="mt-1">
        <i class="pi pi-spinner pi-spin text-sm text-blue-400"></i>
      </div>
      <p v-else class="mt-0.5 text-base text-gray-300 dark:text-gray-600 sm:mt-1 sm:text-lg">—</p>
    </div>
    <div
      class="rounded-lg border border-gray-200 bg-gray-50 p-2 text-center dark:border-gray-700 dark:bg-gray-900 sm:p-3"
    >
      <p
        class="text-[9px] font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500 sm:text-[10px]"
      >
        {{ t('candidates.prescanning') }}
      </p>
      <p
        v-if="prescanningScore != null"
        class="mt-0.5 text-base font-bold sm:mt-1 sm:text-lg"
        :class="scoreColor(normalizeScreeningScore(prescanningScore) ?? 0)"
      >
        {{ prescanningScore }}/10
      </p>
      <p v-else class="mt-0.5 text-base text-gray-300 dark:text-gray-600 sm:mt-1 sm:text-lg">—</p>
    </div>
    <div
      class="rounded-lg border border-gray-200 bg-gray-50 p-2 text-center dark:border-gray-700 dark:bg-gray-900 sm:p-3"
    >
      <p
        class="text-[9px] font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500 sm:text-[10px]"
      >
        {{ t('candidates.interview') }}
      </p>
      <p
        v-if="interviewScore != null"
        class="mt-0.5 text-base font-bold sm:mt-1 sm:text-lg"
        :class="scoreColor(normalizeScreeningScore(interviewScore) ?? 0)"
      >
        {{ interviewScore }}/10
      </p>
      <p v-else class="mt-0.5 text-base text-gray-300 dark:text-gray-600 sm:mt-1 sm:text-lg">—</p>
    </div>
    <div
      class="rounded-lg border-2 p-2 text-center sm:p-3"
      :class="overallScore !== null ? 'border-blue-200 bg-blue-50' : 'border-gray-200 bg-gray-50'"
    >
      <p
        class="text-[9px] font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500 sm:text-[10px]"
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
</template>
