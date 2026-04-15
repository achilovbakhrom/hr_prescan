<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import type { IntegrityFlag, FlagType, Severity } from '../types/integrity.types'

defineProps<{
  flag: IntegrityFlag
  expanded: boolean
}>()

const emit = defineEmits<{ toggle: [id: string] }>()

const { t } = useI18n()

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

const FLAG_TYPE_META: Record<FlagType, { icon: string; label: string; detail: string }> = {
  face_not_visible: {
    icon: '\u{1F464}',
    label: 'Face Not Visible',
    detail: "The candidate's face was not visible in the video feed.",
  },
  multiple_faces: {
    icon: '\u{1F465}',
    label: 'Multiple Faces',
    detail: 'More than one person was detected in the video frame.',
  },
  gaze_deviation: {
    icon: '\u{1F440}',
    label: 'Gaze Deviation',
    detail: "The candidate's gaze deviated significantly from the camera.",
  },
  audio_anomaly: {
    icon: '\u{1F399}\u{FE0F}',
    label: 'Audio Anomaly',
    detail: 'Unusual audio patterns were detected during the interview.',
  },
  cv_inconsistency: {
    icon: '\u{1F4C4}',
    label: 'CV Inconsistency',
    detail: "Discrepancies were found between the candidate's CV and interview answers.",
  },
}

function getFlagMeta(flagType: FlagType) {
  return FLAG_TYPE_META[flagType] ?? { icon: '\u{26A0}\u{FE0F}', label: flagType, detail: '' }
}
function getSeverityConfig(severity: Severity): SeverityConfig {
  return SEVERITY_CONFIG[severity] ?? SEVERITY_CONFIG.low
}

function formatTimestamp(seconds: number | null): string {
  if (seconds === null || seconds === undefined) return ''
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `at ${mins}:${secs.toString().padStart(2, '0')}`
}
</script>

<template>
  <div
    class="overflow-hidden rounded-lg border transition-shadow hover:shadow-sm"
    :class="getSeverityConfig(flag.severity).borderClass"
  >
    <button
      class="flex w-full items-start gap-3 px-4 py-3 text-left"
      :class="getSeverityConfig(flag.severity).bgClass"
      @click="emit('toggle', flag.id)"
    >
      <span class="mt-0.5 shrink-0 text-xl leading-none">{{
        getFlagMeta(flag.flagType).icon
      }}</span>
      <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-sm font-semibold text-gray-800">{{
            t(`interviews.integrity.flagLabels.${flag.flagType}`, getFlagMeta(flag.flagType).label)
          }}</span>
          <Tag
            :value="getSeverityConfig(flag.severity).label"
            :severity="getSeverityConfig(flag.severity).tagSeverity"
            class="shrink-0 !text-[10px]"
          />
          <span
            v-if="flag.timestampSeconds !== null && flag.timestampSeconds !== undefined"
            class="text-xs text-gray-400"
            >{{ formatTimestamp(flag.timestampSeconds) }}</span
          >
        </div>
        <p class="mt-1 line-clamp-1 text-sm text-gray-600">{{ flag.description }}</p>
      </div>
      <span
        class="mt-1 shrink-0 text-gray-400 transition-transform"
        :class="expanded ? 'rotate-180' : ''"
        >&#x25BE;</span
      >
    </button>

    <div
      v-if="expanded"
      class="border-t px-4 py-3 text-sm text-gray-700"
      :class="getSeverityConfig(flag.severity).borderClass"
    >
      <p class="mb-2 font-medium text-gray-500">{{ t('interviews.integrity.details') }}</p>
      <p class="leading-relaxed">{{ flag.description }}</p>
      <p class="mt-2 text-xs text-gray-400">
        {{
          t(`interviews.integrity.flagDetails.${flag.flagType}`, getFlagMeta(flag.flagType).detail)
        }}
      </p>
      <p v-if="flag.createdAt" class="mt-2 text-xs text-gray-400">
        {{ t('interviews.integrity.recorded') }} {{ new Date(flag.createdAt).toLocaleString() }}
      </p>
    </div>
  </div>
</template>
