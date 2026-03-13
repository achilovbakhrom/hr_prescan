<script setup lang="ts">
import ProgressBar from 'primevue/progressbar'
import type { InterviewScore } from '../types/interview.types'

defineProps<{
  scores: InterviewScore[]
}>()

function scoreColor(score: number): string {
  if (score >= 80) return 'text-green-600'
  if (score >= 60) return 'text-blue-600'
  if (score >= 40) return 'text-yellow-600'
  return 'text-red-600'
}
</script>

<template>
  <div class="space-y-4">
    <p v-if="scores.length === 0" class="text-sm text-gray-500">
      No scores available yet.
    </p>

    <div
      v-for="score in scores"
      :key="score.id"
      class="rounded-lg border border-gray-200 p-4"
    >
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium text-gray-700">
          {{ score.criteriaName }}
        </span>
        <span class="text-sm font-bold" :class="scoreColor(score.score)">
          {{ score.score }}/100
        </span>
      </div>

      <ProgressBar
        :value="score.score"
        :show-value="false"
        class="mb-2"
        style="height: 8px"
      />

      <p v-if="score.aiNotes" class="text-xs text-gray-500">
        {{ score.aiNotes }}
      </p>
    </div>
  </div>
</template>
