<script setup lang="ts">
/**
 * TranscriptView — interview transcript with glass/solid message bubbles.
 * Candidate = solid surface-raised; AI = bg-glass-1 with violet tint.
 * Timestamps rendered in Geist Mono (font-mono) per spec §9.
 */
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
  const val = (entry.speaker || entry.role || '').toLowerCase()
  return val === 'ai' || val === 'interviewer'
}

function getSpeakerLabel(entry: TranscriptEntry): string {
  const val = entry.speaker || entry.role || 'Unknown'
  const lower = val.toLowerCase()
  if (lower === 'ai' || lower === 'interviewer') return 'Interviewer'
  if (lower === 'candidate' || lower === 'user') return 'Candidate'
  return val
}
</script>

<template>
  <div class="space-y-3 font-mono">
    <p
      v-if="transcript.length === 0"
      class="text-center text-sm text-[color:var(--color-text-muted)]"
    >
      No transcript available yet.
    </p>

    <div
      v-for="(entry, index) in transcript"
      :key="index"
      class="flex"
      :class="isAi(entry) ? 'justify-start' : 'justify-end'"
    >
      <div
        class="max-w-[80%] rounded-lg px-4 py-2"
        :class="
          isAi(entry)
            ? 'bg-glass-1 border-glass text-[color:var(--color-text-primary)]'
            : 'bg-[color:var(--color-surface-raised)] border border-[color:var(--color-border-soft)] text-[color:var(--color-text-primary)]'
        "
      >
        <div class="mb-1 flex items-center gap-2">
          <span
            class="text-xs font-semibold"
            :class="isAi(entry) ? 'text-[color:var(--color-accent-ai)]' : ''"
            >{{ getSpeakerLabel(entry) }}</span
          >
          <span class="font-mono text-xs text-[color:var(--color-text-muted)]">
            {{ formatTimestamp(entry.timestamp) }}
          </span>
        </div>
        <p class="font-sans text-sm leading-relaxed">{{ entry.text }}</p>
      </div>
    </div>
  </div>
</template>
