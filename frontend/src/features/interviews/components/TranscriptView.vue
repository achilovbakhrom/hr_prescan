<script setup lang="ts">
import type { TranscriptEntry } from '../types/interview.types'

defineProps<{
  transcript: TranscriptEntry[]
}>()

function formatTimestamp(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function isAi(entry: TranscriptEntry): boolean {
  const val = (entry.speaker || (entry as any).role || '').toLowerCase()
  return val === 'ai' || val === 'interviewer'
}

function getSpeakerLabel(entry: TranscriptEntry): string {
  const val = entry.speaker || (entry as any).role || 'Unknown'
  const lower = val.toLowerCase()
  if (lower === 'ai' || lower === 'interviewer') return 'Interviewer'
  if (lower === 'candidate' || lower === 'user') return 'Candidate'
  return val
}
</script>

<template>
  <div class="space-y-3">
    <p v-if="transcript.length === 0" class="text-sm text-gray-500">
      No transcript available yet.
    </p>

    <div
      v-for="(entry, index) in transcript"
      :key="index"
      class="flex gap-3"
      :class="isAi(entry) ? 'justify-start' : 'justify-end'"
    >
      <div
        class="max-w-[75%] rounded-lg px-4 py-2"
        :class="
          isAi(entry)
            ? 'bg-gray-100 text-gray-800'
            : 'bg-blue-50 text-blue-900'
        "
      >
        <div class="mb-1 flex items-center gap-2">
          <span class="text-xs font-semibold">{{ getSpeakerLabel(entry) }}</span>
          <span class="text-xs text-gray-400">
            {{ formatTimestamp(entry.timestamp) }}
          </span>
        </div>
        <p class="text-sm">{{ entry.text }}</p>
      </div>
    </div>
  </div>
</template>
