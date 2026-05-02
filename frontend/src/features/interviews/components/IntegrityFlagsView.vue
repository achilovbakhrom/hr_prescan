<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import type { IntegrityFlag, IntegritySeverity } from '../types/interview.types'

defineProps<{
  flags: IntegrityFlag[]
}>()

const { t } = useI18n()

const severityConfig: Record<IntegritySeverity, { severity: 'success' | 'warn' | 'danger' }> = {
  low: { severity: 'success' },
  medium: { severity: 'warn' },
  high: { severity: 'danger' },
}

function formatFlagType(flagType: string): string {
  return flagType
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function formatTimestamp(seconds: number | null): string {
  if (seconds === null) return ''
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return t('interviews.integrity.atTimestamp', {
    time: `${mins}:${secs.toString().padStart(2, '0')}`,
  })
}
</script>

<template>
  <div class="space-y-3">
    <p v-if="flags.length === 0" class="text-sm text-gray-500">
      {{ t('interviews.integrity.noFlagsShort') }}
    </p>

    <div
      v-for="flag in flags"
      :key="flag.id"
      class="flex items-start gap-3 rounded-lg border border-gray-200 dark:border-gray-700 p-4"
    >
      <Tag
        :value="t(`interviews.integrity.severity.${flag.severity}`)"
        :severity="severityConfig[flag.severity].severity"
        class="shrink-0"
      />
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-gray-800">
            {{ formatFlagType(flag.flagType) }}
          </span>
          <span v-if="flag.timestampSeconds !== null" class="text-xs text-gray-400">
            {{ formatTimestamp(flag.timestampSeconds) }}
          </span>
        </div>
        <p class="mt-1 text-sm text-gray-600">{{ flag.description }}</p>
      </div>
    </div>
  </div>
</template>
