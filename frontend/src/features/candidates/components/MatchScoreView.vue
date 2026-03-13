<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  overallScore: number | null
  matchDetails: Record<string, number>
}>()

const sortedCriteria = computed(() => {
  return Object.entries(props.matchDetails).sort(([, a], [, b]) => b - a)
})

function scoreColor(score: number): string {
  if (score >= 80) return 'bg-green-500'
  if (score >= 60) return 'bg-blue-500'
  if (score >= 40) return 'bg-yellow-500'
  return 'bg-red-500'
}

function scoreBgColor(score: number): string {
  if (score >= 80) return 'bg-green-100'
  if (score >= 60) return 'bg-blue-100'
  if (score >= 40) return 'bg-yellow-100'
  return 'bg-red-100'
}
</script>

<template>
  <div class="space-y-6">
    <!-- Overall Score -->
    <div class="text-center">
      <p class="mb-2 text-sm font-semibold text-gray-600">Overall Match</p>
      <div
        v-if="props.overallScore !== null"
        class="inline-flex h-24 w-24 items-center justify-center rounded-full"
        :class="scoreBgColor(props.overallScore)"
      >
        <span class="text-2xl font-bold">{{ props.overallScore }}%</span>
      </div>
      <p v-else class="text-gray-400">Score pending</p>
    </div>

    <!-- Per-criteria Breakdown -->
    <div v-if="sortedCriteria.length > 0">
      <h3 class="mb-3 text-sm font-semibold text-gray-600">
        Criteria Breakdown
      </h3>
      <div class="space-y-3">
        <div v-for="[name, score] in sortedCriteria" :key="name">
          <div class="mb-1 flex items-center justify-between">
            <span class="text-sm font-medium text-gray-700">{{ name }}</span>
            <span class="text-sm font-semibold">{{ score }}%</span>
          </div>
          <div class="h-2.5 w-full rounded-full bg-gray-200">
            <div
              class="h-2.5 rounded-full transition-all"
              :class="scoreColor(score)"
              :style="{ width: `${score}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>
    <p
      v-else-if="props.overallScore === null"
      class="text-center text-sm text-gray-400"
    >
      Match analysis will be available after CV processing
    </p>
  </div>
</template>
