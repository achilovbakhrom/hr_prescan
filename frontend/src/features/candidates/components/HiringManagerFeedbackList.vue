<script setup lang="ts">
import type { HiringManagerFeedback } from '../types/candidate.types'

defineProps<{
  feedback: HiringManagerFeedback[]
}>()

function formatDate(value: string): string {
  return new Date(value).toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function recommendationClass(value: string): string {
  if (value === 'advance') return 'bg-green-50 text-green-700'
  if (value === 'reject') return 'bg-red-50 text-red-700'
  return 'bg-yellow-50 text-yellow-700'
}
</script>

<template>
  <div class="space-y-3">
    <h3 class="text-sm font-semibold text-gray-600">Hiring manager feedback</h3>
    <p v-if="!feedback.length" class="text-sm text-gray-400">No feedback submitted yet.</p>
    <div
      v-for="item in feedback"
      :key="item.id"
      class="rounded-lg border border-gray-200 dark:border-gray-700 p-3"
    >
      <div class="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p class="text-sm font-medium text-gray-800">{{ item.reviewerName }}</p>
          <p class="text-xs text-gray-500">
            {{ item.reviewerRole || 'Hiring manager' }} · {{ formatDate(item.createdAt) }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <span
            class="rounded-full px-2.5 py-1 text-xs font-semibold"
            :class="recommendationClass(item.recommendation)"
          >
            {{ item.recommendation }}
          </span>
          <span v-if="item.rating" class="text-xs font-medium text-gray-500">
            {{ item.rating }}/5
          </span>
        </div>
      </div>
      <p v-if="item.comment" class="mt-2 whitespace-pre-wrap text-sm text-gray-600">
        {{ item.comment }}
      </p>
    </div>
  </div>
</template>
