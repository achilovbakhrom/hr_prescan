<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import TranslatableText from '@/shared/components/TranslatableText.vue'

defineProps<{
  matchScore: number
  matchDetails?: MatchDetails | null
  matchNotesTranslations?: Record<string, string>
  applicationId?: string
}>()

const { t } = useI18n()

interface MatchDetails {
  overall?: number
  criteria_scores?: Record<string, number>
  notes?: string
  matching_skills?: string[]
  missing_skills?: string[]
}

function formatCriteriaName(name: string): string {
  return name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function scoreBg(score: number): string {
  if (score >= 80) return 'bg-green-100 text-green-700'
  if (score >= 60) return 'bg-blue-100 text-blue-700'
  if (score >= 40) return 'bg-yellow-100 text-yellow-700'
  return 'bg-red-100 text-red-700'
}
</script>

<template>
  <div class="mb-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
    <div class="flex items-center gap-4">
      <div
        class="flex h-16 w-16 shrink-0 items-center justify-center rounded-full"
        :class="scoreBg(matchScore)"
      >
        <span class="text-xl font-bold">{{ matchScore }}%</span>
      </div>
      <div class="flex-1">
        <p class="text-sm font-semibold text-gray-700">{{ t('candidates.matchScore') }}</p>
        <TranslatableText
          v-if="matchDetails?.notes && applicationId"
          :text="matchDetails.notes"
          :translations="matchNotesTranslations || {}"
          model="application"
          :object-id="applicationId"
          field="match_notes"
        >
          <template #default="{ text }"
            ><p class="mt-0.5 text-xs text-gray-500">{{ text }}</p></template
          >
        </TranslatableText>
        <p v-else-if="matchDetails?.notes" class="mt-0.5 text-xs text-gray-500">
          {{ matchDetails.notes }}
        </p>
      </div>
    </div>

    <div v-if="matchDetails?.criteria_scores" class="mt-3 grid grid-cols-3 gap-2">
      <div
        v-for="(score, name) in matchDetails.criteria_scores"
        :key="name"
        class="rounded-lg bg-gray-50 dark:bg-gray-900 p-2 text-center"
      >
        <p class="text-xs text-gray-500">{{ formatCriteriaName(String(name)) }}</p>
        <p
          class="text-sm font-bold"
          :class="score >= 70 ? 'text-green-600' : score >= 40 ? 'text-yellow-600' : 'text-red-600'"
        >
          {{ score }}%
        </p>
      </div>
    </div>

    <div
      v-if="matchDetails?.matching_skills?.length || matchDetails?.missing_skills?.length"
      class="mt-3 space-y-2"
    >
      <div v-if="matchDetails?.matching_skills?.length">
        <p class="mb-1 text-xs font-medium text-gray-500">
          {{ t('candidates.cvData.matchingSkills') }}
        </p>
        <div class="flex flex-wrap gap-1">
          <Tag
            v-for="s in matchDetails.matching_skills"
            :key="s"
            :value="s"
            severity="success"
            class="!text-[10px]"
          />
        </div>
      </div>
      <div v-if="matchDetails?.missing_skills?.length">
        <p class="mb-1 text-xs font-medium text-gray-500">
          {{ t('candidates.cvData.missingSkills') }}
        </p>
        <div class="flex flex-wrap gap-1">
          <Tag
            v-for="s in matchDetails.missing_skills"
            :key="s"
            :value="s"
            severity="danger"
            class="!text-[10px]"
          />
        </div>
      </div>
    </div>
  </div>
</template>
