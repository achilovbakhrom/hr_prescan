<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ProgressBar from 'primevue/progressbar'
import type { Completeness } from '../types/cv-builder.types'

const props = defineProps<{
  completeness: Completeness
}>()

const { t } = useI18n()

interface SectionStatus {
  label: string
  done: boolean
}

const sections = computed<SectionStatus[]>(() => [
  { label: t('cvBuilder.completeness.personal'), done: props.completeness.sections.personal },
  { label: t('cvBuilder.completeness.summary'), done: props.completeness.sections.summary },
  { label: t('cvBuilder.completeness.experience'), done: props.completeness.sections.experience },
  { label: t('cvBuilder.completeness.education'), done: props.completeness.sections.education },
  { label: t('cvBuilder.completeness.skills'), done: props.completeness.sections.skills },
  { label: t('cvBuilder.completeness.languages'), done: props.completeness.sections.languages },
])

const progressColor = computed(() => {
  const score = props.completeness.score
  if (score >= 80) return 'bg-green-500'
  if (score >= 50) return 'bg-yellow-500'
  return 'bg-red-500'
})
</script>

<template>
  <div class="rounded-lg bg-white p-4 shadow-sm sm:p-6">
    <div class="mb-3 flex items-center justify-between">
      <h2 class="text-base font-semibold text-gray-900 sm:text-lg">
        {{ t('cvBuilder.completeness.title') }}
      </h2>
      <span
        class="rounded-full px-2.5 py-0.5 text-xs font-medium"
        :class="progressColor.replace('bg-', 'bg-') + '/10 ' + progressColor.replace('bg-', 'text-')"
      >
        {{ completeness.score }}%
      </span>
    </div>

    <ProgressBar
      :value="completeness.score"
      :showValue="false"
      class="mb-4 h-2"
    />

    <div class="grid grid-cols-2 gap-2 sm:grid-cols-3">
      <div
        v-for="section in sections"
        :key="section.label"
        class="flex items-center gap-2 text-sm"
      >
        <i
          class="text-xs"
          :class="section.done ? 'pi pi-check-circle text-green-500' : 'pi pi-circle text-gray-300'"
        ></i>
        <span :class="section.done ? 'text-gray-700' : 'text-gray-400'">
          {{ section.label }}
        </span>
      </div>
    </div>
  </div>
</template>
