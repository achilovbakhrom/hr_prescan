<script setup lang="ts">
import { computed, ref } from 'vue'
import Tag from 'primevue/tag'
import type { IntegrityFlag, FlagType, Severity } from '../types/integrity.types'

const props = defineProps<{
  flags: IntegrityFlag[]
}>()

// Track which flags are expanded
const expandedFlags = ref<Set<string>>(new Set())

function toggleExpand(id: string): void {
  if (expandedFlags.value.has(id)) {
    expandedFlags.value.delete(id)
  } else {
    expandedFlags.value.add(id)
  }
}

function isExpanded(id: string): boolean {
  return expandedFlags.value.has(id)
}

// ---------------------------------------------------------------------------
// Severity config
// ---------------------------------------------------------------------------

type SeverityConfig = {
  tagSeverity: 'success' | 'warn' | 'danger' | 'secondary'
  bgClass: string
  borderClass: string
  textClass: string
  label: string
}

const SEVERITY_CONFIG: Record<Severity, SeverityConfig> = {
  low: {
    tagSeverity: 'success',
    bgClass: 'bg-green-50',
    borderClass: 'border-green-200',
    textClass: 'text-green-700',
    label: 'LOW',
  },
  medium: {
    tagSeverity: 'warn',
    bgClass: 'bg-yellow-50',
    borderClass: 'border-yellow-200',
    textClass: 'text-yellow-700',
    label: 'MEDIUM',
  },
  high: {
    tagSeverity: 'danger',
    bgClass: 'bg-red-50',
    borderClass: 'border-red-200',
    textClass: 'text-red-700',
    label: 'HIGH',
  },
}

// ---------------------------------------------------------------------------
// Flag type icons and labels
// ---------------------------------------------------------------------------

const FLAG_TYPE_META: Record<FlagType, { icon: string; label: string; detail: string }> = {
  face_not_visible: {
    icon: '👤',
    label: 'Face Not Visible',
    detail: "The candidate's face was not visible in the video feed.",
  },
  multiple_faces: {
    icon: '👥',
    label: 'Multiple Faces',
    detail: 'More than one person was detected in the video frame.',
  },
  gaze_deviation: {
    icon: '👀',
    label: 'Gaze Deviation',
    detail: "The candidate's gaze deviated significantly from the camera.",
  },
  audio_anomaly: {
    icon: '🎙️',
    label: 'Audio Anomaly',
    detail: 'Unusual audio patterns were detected during the interview.',
  },
  cv_inconsistency: {
    icon: '📄',
    label: 'CV Inconsistency',
    detail: "Discrepancies were found between the candidate's CV and interview answers.",
  },
}

// ---------------------------------------------------------------------------
// Overall integrity score
// ---------------------------------------------------------------------------

const integrityScore = computed<number>(() => {
  if (props.flags.length === 0) return 100

  const penalties: Record<Severity, number> = {
    low: 5,
    medium: 15,
    high: 25,
  }

  const totalPenalty = props.flags.reduce((acc, flag) => {
    return acc + (penalties[flag.severity] ?? 5)
  }, 0)

  return Math.max(0, 100 - totalPenalty)
})

const scoreColor = computed<string>(() => {
  if (integrityScore.value >= 80) return 'text-green-600'
  if (integrityScore.value >= 60) return 'text-yellow-600'
  if (integrityScore.value >= 40) return 'text-orange-600'
  return 'text-red-600'
})

const scoreLabel = computed<string>(() => {
  if (integrityScore.value >= 80) return 'Good'
  if (integrityScore.value >= 60) return 'Fair'
  if (integrityScore.value >= 40) return 'Poor'
  return 'Critical'
})

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatTimestamp(seconds: number | null): string {
  if (seconds === null || seconds === undefined) return ''
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `at ${mins}:${secs.toString().padStart(2, '0')}`
}

function getFlagMeta(flagType: FlagType) {
  return FLAG_TYPE_META[flagType] ?? { icon: '⚠️', label: flagType, detail: '' }
}

function getSeverityConfig(severity: Severity): SeverityConfig {
  return SEVERITY_CONFIG[severity] ?? SEVERITY_CONFIG.low
}
</script>

<template>
  <div class="space-y-4">
    <!-- Overall integrity score banner -->
    <div
      class="flex items-center justify-between rounded-xl border border-gray-200 bg-gray-50 px-5 py-4"
    >
      <div>
        <p class="text-sm font-medium text-gray-500">Overall Integrity Score</p>
        <p class="mt-0.5 text-xs text-gray-400">
          Based on {{ flags.length }} flag{{ flags.length !== 1 ? 's' : '' }} detected
        </p>
      </div>
      <div class="text-right">
        <span class="text-3xl font-bold" :class="scoreColor">
          {{ integrityScore }}
        </span>
        <span class="ml-1 text-sm text-gray-400">/100</span>
        <p class="mt-0.5 text-xs font-medium" :class="scoreColor">{{ scoreLabel }}</p>
      </div>
    </div>

    <!-- No flags state -->
    <p v-if="flags.length === 0" class="py-2 text-center text-sm text-gray-500">
      No integrity flags detected. The interview passed all checks.
    </p>

    <!-- Flag list -->
    <div
      v-for="flag in flags"
      :key="flag.id"
      class="overflow-hidden rounded-lg border transition-shadow hover:shadow-sm"
      :class="getSeverityConfig(flag.severity).borderClass"
    >
      <!-- Flag header (always visible) -->
      <button
        class="flex w-full items-start gap-3 px-4 py-3 text-left"
        :class="getSeverityConfig(flag.severity).bgClass"
        @click="toggleExpand(flag.id)"
      >
        <!-- Icon -->
        <span class="mt-0.5 shrink-0 text-xl leading-none">
          {{ getFlagMeta(flag.flagType).icon }}
        </span>

        <!-- Content -->
        <div class="min-w-0 flex-1">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-sm font-semibold text-gray-800">
              {{ getFlagMeta(flag.flagType).label }}
            </span>
            <Tag
              :value="getSeverityConfig(flag.severity).label"
              :severity="getSeverityConfig(flag.severity).tagSeverity"
              class="shrink-0 !text-[10px]"
            />
            <span
              v-if="flag.timestampSeconds !== null && flag.timestampSeconds !== undefined"
              class="text-xs text-gray-400"
            >
              {{ formatTimestamp(flag.timestampSeconds) }}
            </span>
          </div>

          <!-- Short description (always shown) -->
          <p class="mt-1 line-clamp-1 text-sm text-gray-600">
            {{ flag.description }}
          </p>
        </div>

        <!-- Expand chevron -->
        <span
          class="mt-1 shrink-0 text-gray-400 transition-transform"
          :class="isExpanded(flag.id) ? 'rotate-180' : ''"
        >
          ▾
        </span>
      </button>

      <!-- Expanded details -->
      <div
        v-if="isExpanded(flag.id)"
        class="border-t px-4 py-3 text-sm text-gray-700"
        :class="getSeverityConfig(flag.severity).borderClass"
      >
        <p class="mb-2 font-medium text-gray-500">Details</p>
        <p class="leading-relaxed">{{ flag.description }}</p>
        <p class="mt-2 text-xs text-gray-400">
          {{ getFlagMeta(flag.flagType).detail }}
        </p>
        <p v-if="flag.createdAt" class="mt-2 text-xs text-gray-400">
          Recorded: {{ new Date(flag.createdAt).toLocaleString() }}
        </p>
      </div>
    </div>
  </div>
</template>
