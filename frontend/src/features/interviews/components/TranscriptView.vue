<script setup lang="ts">
import { ref, computed } from 'vue'
import type { TranscriptEntry } from '../types/interview.types'

const props = defineProps<{
  transcript: TranscriptEntry[]
}>()

const searchQuery = ref('')

const filteredTranscript = computed(() => {
  if (!searchQuery.value.trim()) return props.transcript
  const query = searchQuery.value.toLowerCase()
  return props.transcript.filter(
    (entry) =>
      entry.text.toLowerCase().includes(query) ||
      entry.speaker.toLowerCase().includes(query),
  )
})

function formatTimestamp(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

function isAi(speaker: string): boolean {
  return speaker.toLowerCase() === 'ai' || speaker.toLowerCase() === 'interviewer'
}
</script>

<template>
  <div class="space-y-3">
    <div class="relative">
      <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search transcript..."
        class="w-full rounded-lg border border-gray-300 py-2 pl-9 pr-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />
    </div>

    <p v-if="transcript.length === 0" class="text-sm text-gray-500">
      No transcript available yet.
    </p>

    <p
      v-else-if="filteredTranscript.length === 0"
      class="text-sm text-gray-500"
    >
      No matches found for "{{ searchQuery }}"
    </p>

    <div
      v-for="(entry, index) in filteredTranscript"
      :key="index"
      class="flex gap-3"
      :class="isAi(entry.speaker) ? 'justify-start' : 'justify-end'"
    >
      <div
        class="max-w-[75%] rounded-lg px-4 py-2"
        :class="
          isAi(entry.speaker)
            ? 'bg-gray-100 text-gray-800'
            : 'bg-blue-50 text-blue-900'
        "
      >
        <div class="mb-1 flex items-center gap-2">
          <span
            class="text-xs font-semibold"
            :class="isAi(entry.speaker) ? 'text-gray-600' : 'text-blue-700'"
          >
            {{ entry.speaker }}
          </span>
          <span class="rounded bg-gray-200 px-1.5 py-0.5 text-xs tabular-nums text-gray-500">
            {{ formatTimestamp(entry.timestamp) }}
          </span>
        </div>
        <p class="text-sm">{{ entry.text }}</p>
      </div>
    </div>
  </div>
</template>
