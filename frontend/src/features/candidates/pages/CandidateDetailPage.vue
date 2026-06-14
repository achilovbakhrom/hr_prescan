<script setup lang="ts">
/**
 * CandidateDetailPage — crown jewel of HR workflow.
 * Header action bar + CandidateDetailTabs (overview / cv / prescanning /
 * interview / analysis / notes) in left column, CandidateScoreCard rail
 * on the right (desktop only). Spec §9 Candidates (HR detail).
 */
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { extractErrorMessage } from '@/shared/api/errors'
import { useCandidateStore } from '../stores/candidate.store'
import { useInterviewData } from '../composables/useInterviewData'
import CandidateActions from '../components/CandidateActions.vue'
import CandidateDetailHero from '../components/CandidateDetailHero.vue'
import CandidateDetailTabs from '../components/CandidateDetailTabs.vue'
import { candidateService } from '../services/candidate.service'
import { calculateOverallScore } from '../utils/score'
import type { ApplicationStatus } from '../types/candidate.types'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const candidateStore = useCandidateStore()
const {
  prescanningScore,
  interviewScore,
  aiSummary,
  aiSummaryTranslations,
  aiSummaryInterviewId,
  analysisSessions,
  fetchInterviewData,
} = useInterviewData()

const candidateId = computed(() => route.params.id as string)
const candidate = computed(() => candidateStore.currentCandidate)
const hasInterview = computed(() => candidate.value?.interviewEnabled ?? false)
const effectivePrescanningScore = computed(
  () => prescanningScore.value ?? candidate.value?.prescanningScore ?? null,
)
const effectiveInterviewScore = computed(
  () => interviewScore.value ?? candidate.value?.interviewScore ?? null,
)
const overallScore = computed(() => {
  if (!candidate.value) return null
  return calculateOverallScore({
    cvMatchScore: candidate.value.matchScore,
    prescanningScore: effectivePrescanningScore.value,
    interviewScore: effectiveInterviewScore.value,
  })
})

const tabNames = computed(() => {
  const base = ['overview', 'cv', 'prescanning']
  if (hasInterview.value) base.push('interview')
  base.push('analysis', 'notes')
  return base
})
const activeTab = computed({
  get: () => {
    const idx = tabNames.value.indexOf(route.query.tab as string)
    return idx >= 0 ? idx : 0
  },
  set: (val: number) => {
    router.replace({ query: { ...route.query, tab: tabNames.value[val] } })
  },
})

onMounted(async () => {
  await candidateStore.fetchCandidateDetail(candidateId.value)
  await fetchInterviewData(candidateId.value, candidate.value?.interviewEnabled ?? false)
})

async function handleStatusChange(status: ApplicationStatus): Promise<void> {
  await candidateStore.updateStatus(candidateId.value, status).catch(() => {})
}
async function handleSaveNotes(note: string): Promise<void> {
  await candidateStore.addNote(candidateId.value, note).catch(() => {})
}
async function handleDownloadCv(): Promise<void> {
  if (!candidate.value?.cvFile) return
  try {
    const { url } = await candidateService.getCvDownloadUrl(candidateId.value)
    window.open(url, '_blank')
  } catch {
    window.open(candidate.value.cvFile, '_blank')
  }
}
async function handleResetScreening(sessionType: 'prescanning' | 'interview'): Promise<void> {
  if (!candidate.value) return
  candidateStore.loading = true
  candidateStore.error = null
  try {
    candidateStore.currentCandidate = await candidateService.resetScreening(
      candidateId.value,
      sessionType,
    )
    await fetchInterviewData(candidateId.value, candidate.value?.interviewEnabled ?? false)
  } catch (err: unknown) {
    candidateStore.error = extractErrorMessage(err)
  } finally {
    candidateStore.loading = false
  }
}

function handleShareTokenRotated(token: string): void {
  if (candidateStore.currentCandidate) {
    candidateStore.currentCandidate.hiringManagerToken = token
  }
}
</script>

<template>
  <div class="space-y-4">
    <button
      class="inline-flex items-center gap-2 text-sm text-[color:var(--color-text-muted)] transition-colors hover:text-[color:var(--color-text-primary)]"
      @click="router.back()"
    >
      <i class="pi pi-arrow-left"></i> {{ t('nav.candidates') }}
    </button>

    <p v-if="candidateStore.error" class="text-sm text-[color:var(--color-danger)]">
      {{ candidateStore.error }}
    </p>
    <div v-if="!candidate && candidateStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <template v-else-if="candidate">
      <CandidateDetailHero :candidate="candidate" :overall-score="overallScore">
        <template #actions>
          <CandidateActions
            :candidate-id="candidate.id"
            :candidate-name="candidate.candidateName"
            :candidate-email="candidate.candidateEmail"
            :current-status="candidate.status"
            :loading="candidateStore.loading"
            :interview-enabled="candidate.interviewEnabled"
            :hiring-manager-token="candidate.hiringManagerToken"
            @status-change="handleStatusChange"
            @reset-screening="handleResetScreening"
            @share-token-rotated="handleShareTokenRotated"
          />
        </template>
      </CandidateDetailHero>

      <CandidateDetailTabs
        :candidate="candidate"
        :loading="candidateStore.loading"
        :active-tab="activeTab"
        :prescanning-score="effectivePrescanningScore"
        :interview-score="effectiveInterviewScore"
        :ai-summary="aiSummary"
        :ai-summary-translations="aiSummaryTranslations"
        :ai-summary-interview-id="aiSummaryInterviewId"
        :analysis-sessions="analysisSessions"
        @update:active-tab="activeTab = $event"
        @update:ai-summary-translations="aiSummaryTranslations = $event"
        @save-notes="handleSaveNotes"
        @download-cv="handleDownloadCv"
      />
    </template>
  </div>
</template>
