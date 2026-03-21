<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ProgressBar from 'primevue/progressbar'
import { apiClient } from '@/shared/api/client'
import type { InterviewScore, IntegrityFlag } from '@/shared/types/interview.types'

interface CandidateInterviewScores {
  overallScore: number | null
  scores: InterviewScore[]
  integrityFlags: IntegrityFlag[]
}

const props = defineProps<{
  candidateId: string
}>()

const data = ref<CandidateInterviewScores | null>(null)
const loading = ref(false)

function scoreColor(score: number): string {
  if (score >= 80) return 'text-green-600'
  if (score >= 60) return 'text-blue-600'
  if (score >= 40) return 'text-yellow-600'
  return 'text-red-600'
}

function severityColor(severity: string): string {
  if (severity === 'high') return 'bg-red-100 text-red-700'
  if (severity === 'medium') return 'bg-yellow-100 text-yellow-700'
  return 'bg-gray-100 text-gray-700'
}

onMounted(async () => {
  loading.value = true
  try {
    const response = await apiClient.get<CandidateInterviewScores>(
      `/candidates/${props.candidateId}/interview-scores`,
    )
    data.value = response.data
  } catch {
    // Scores may not be available yet
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <h3 class="mb-3 text-sm font-semibold text-gray-600">
      Interview Performance
    </h3>

    <div v-if="loading" class="py-4 text-center">
      <i class="pi pi-spinner pi-spin text-xl text-gray-400"></i>
    </div>

    <div v-else-if="!data || data.scores.length === 0">
      <p class="text-sm text-gray-400">
        Interview scores will appear here after the interview is completed.
      </p>
    </div>

    <template v-else>
      <div
        v-if="data.overallScore !== null"
        class="mb-4 rounded-lg bg-blue-50 p-4 text-center"
      >
        <p class="text-xs font-medium text-blue-600">Overall Interview Score</p>
        <p class="text-3xl font-bold" :class="scoreColor(data.overallScore)">
          {{ data.overallScore }}/100
        </p>
      </div>

      <div class="space-y-3">
        <div
          v-for="score in data.scores"
          :key="score.id"
          class="rounded-lg border border-gray-200 p-3"
        >
          <div class="mb-1.5 flex items-center justify-between">
            <span class="text-sm font-medium text-gray-700">
              {{ score.criteriaName }}
            </span>
            <span class="text-sm font-bold" :class="scoreColor(score.score)">
              {{ score.score }}/100
            </span>
          </div>
          <ProgressBar
            :value="score.score"
            :show-value="false"
            style="height: 6px"
          />
          <p v-if="score.aiNotes" class="mt-1.5 text-xs text-gray-500">
            {{ score.aiNotes }}
          </p>
        </div>
      </div>

      <div
        v-if="data.integrityFlags.length > 0"
        class="mt-4"
      >
        <h4 class="mb-2 text-xs font-semibold text-gray-500">
          Integrity Flags
        </h4>
        <div class="space-y-1.5">
          <div
            v-for="flag in data.integrityFlags"
            :key="flag.id"
            class="flex items-center gap-2 rounded px-2 py-1 text-xs"
            :class="severityColor(flag.severity)"
          >
            <i class="pi pi-exclamation-triangle"></i>
            <span>{{ flag.description }}</span>
            <span class="ml-auto font-medium uppercase">{{ flag.severity }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
