<script setup lang="ts">
import { ref, toRef } from 'vue'
import { useI18n } from 'vue-i18n'
import IntegrityFlagItem from './IntegrityFlagItem.vue'
import { useIntegrityScore } from '../composables/useIntegrityScore'
import type { IntegrityFlag } from '../types/integrity.types'

const props = defineProps<{
  flags: IntegrityFlag[]
}>()

const { t } = useI18n()

const expandedFlags = ref<Set<string>>(new Set())
const { integrityScore, scoreColor, scoreLabel } = useIntegrityScore(toRef(props, 'flags'))

function toggleExpand(id: string): void {
  if (expandedFlags.value.has(id)) expandedFlags.value.delete(id)
  else expandedFlags.value.add(id)
}
</script>

<template>
  <div class="space-y-4">
    <div
      class="flex items-center justify-between rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 px-5 py-4"
    >
      <div>
        <p class="text-sm font-medium text-gray-500">
          {{ t('interviews.integrity.overallScore') }}
        </p>
        <p class="mt-0.5 text-xs text-gray-400">
          {{ t('interviews.integrity.flagsDetected', { count: flags.length }) }}
        </p>
      </div>
      <div class="text-right">
        <span class="text-3xl font-bold" :class="scoreColor">{{ integrityScore }}</span>
        <span class="ml-1 text-sm text-gray-400">/100</span>
        <p class="mt-0.5 text-xs font-medium" :class="scoreColor">
          {{ t(`interviews.integrity.scoreLabels.${scoreLabel}`) }}
        </p>
      </div>
    </div>

    <p v-if="flags.length === 0" class="py-2 text-center text-sm text-gray-500">
      {{ t('interviews.integrity.noFlags') }}
    </p>

    <IntegrityFlagItem
      v-for="flag in flags"
      :key="flag.id"
      :flag="flag"
      :expanded="expandedFlags.has(flag.id)"
      @toggle="toggleExpand"
    />
  </div>
</template>
