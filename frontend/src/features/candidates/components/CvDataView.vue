<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import CvMatchScoreCard from './CvMatchScoreCard.vue'
import CvParsedSections from './CvParsedSections.vue'

interface MatchDetails {
  overall?: number
  criteria_scores?: Record<string, number>
  notes?: string
  matching_skills?: string[]
  missing_skills?: string[]
}

const props = defineProps<{
  data: Record<string, unknown> | null
  cvFile?: string
  cvFilename?: string
  matchScore?: number | null
  matchDetails?: MatchDetails | null
  matchNotesTranslations?: Record<string, string>
  cvSummaryTranslations?: Record<string, string>
  applicationId?: string
}>()

const emit = defineEmits<{ downloadCv: [] }>()

const { t } = useI18n()

const hasData = computed(() => {
  if (!props.data) return false
  const skills = (props.data.skills as string[]) || []
  const experience = (props.data.experience as unknown[]) || []
  const education = (props.data.education as unknown[]) || []
  const summary = (props.data.summary as string) || ''
  return skills.length > 0 || experience.length > 0 || education.length > 0 || !!summary
})
</script>

<template>
  <div
    v-if="props.cvFile"
    class="mb-4 flex items-center gap-3 rounded-lg border border-gray-200 bg-gray-50 p-3"
  >
    <i class="pi pi-file-pdf text-2xl text-red-500"></i>
    <div class="min-w-0 flex-1">
      <p class="truncate text-sm font-medium text-gray-700">
        {{ props.cvFilename || t('candidates.cvData.file') }}
      </p>
      <p class="text-xs text-gray-400">{{ t('candidates.cvData.clickToDownload') }}</p>
    </div>
    <Button
      :label="t('candidates.cv')"
      icon="pi pi-download"
      size="small"
      outlined
      @click="emit('downloadCv')"
    />
  </div>

  <div
    v-if="props.cvFile && (props.matchScore === null || props.matchScore === undefined) && !hasData"
    class="mb-4 flex items-center gap-3 rounded-lg border border-blue-200 bg-blue-50 p-4"
  >
    <i class="pi pi-spinner pi-spin text-lg text-blue-500"></i>
    <div>
      <p class="text-sm font-medium text-blue-800">{{ t('candidates.cvData.analyzing') }}</p>
      <p class="text-xs text-blue-600">{{ t('candidates.cvData.extracting') }}</p>
    </div>
  </div>

  <CvMatchScoreCard
    v-if="props.matchScore !== null && props.matchScore !== undefined"
    :match-score="props.matchScore"
    :match-details="props.matchDetails"
    :match-notes-translations="props.matchNotesTranslations"
    :application-id="props.applicationId"
  />

  <div v-if="!hasData" class="py-8 text-center text-gray-400">
    <i class="pi pi-file mb-2 text-3xl"></i>
    <p>{{ t('candidates.cvData.notParsed') }}</p>
  </div>

  <CvParsedSections
    v-if="hasData && props.data"
    :data="props.data"
    :cv-summary-translations="props.cvSummaryTranslations"
    :application-id="props.applicationId"
  />
</template>
