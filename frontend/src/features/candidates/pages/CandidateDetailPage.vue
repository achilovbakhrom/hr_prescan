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
import GlassCard from '@/shared/components/GlassCard.vue'
import { useCandidateStore } from '../stores/candidate.store'
import { useInterviewData } from '../composables/useInterviewData'
import CandidateActions from '../components/CandidateActions.vue'
import CandidateScoreCard from '../components/CandidateScoreCard.vue'
import CandidateDetailTabs from '../components/CandidateDetailTabs.vue'
import { candidateService } from '../services/candidate.service'
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
  fetchInterviewData,
} = useInterviewData()

const candidateId = computed(() => route.params.id as string)
const candidate = computed(() => candidateStore.currentCandidate)
const hasInterview = computed(() => candidate.value?.interviewEnabled ?? false)

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
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-2 sm:gap-3">
      <button
        class="shrink-0 rounded-lg p-1.5 text-[color:var(--color-text-muted)] transition-colors hover:bg-[color:var(--color-surface-sunken)] hover:text-[color:var(--color-text-primary)]"
        @click="router.back()"
      >
        <i class="pi pi-arrow-left"></i>
      </button>
      <div class="min-w-0 flex-1">
        <h1
          class="truncate text-lg font-bold text-[color:var(--color-text-primary)] sm:text-xl md:text-2xl"
        >
          {{ candidate?.candidateName ?? t('common.loading') }}
        </h1>
        <p
          v-if="candidate"
          class="truncate text-xs text-[color:var(--color-text-muted)] sm:text-sm"
        >
          {{ candidate.vacancyTitle }}
        </p>
      </div>
    </div>

    <p v-if="candidateStore.error" class="text-sm text-[color:var(--color-danger)]">
      {{ candidateStore.error }}
    </p>
    <div v-if="!candidate && candidateStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <template v-else-if="candidate">
      <GlassCard class="!p-3">
        <CandidateActions
          :candidate-id="candidate.id"
          :candidate-name="candidate.candidateName"
          :candidate-email="candidate.candidateEmail"
          :vacancy-id="candidate.vacancyId"
          :current-status="candidate.status"
          :loading="candidateStore.loading"
          @status-change="handleStatusChange"
        />
      </GlassCard>

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_20rem]">
        <div class="min-w-0">
          <CandidateDetailTabs
            :candidate="candidate"
            :loading="candidateStore.loading"
            :active-tab="activeTab"
            :prescanning-score="prescanningScore"
            :interview-score="interviewScore"
            :ai-summary="aiSummary"
            :ai-summary-translations="aiSummaryTranslations"
            :ai-summary-interview-id="aiSummaryInterviewId"
            @update:active-tab="activeTab = $event"
            @update:ai-summary-translations="aiSummaryTranslations = $event"
            @save-notes="handleSaveNotes"
            @download-cv="handleDownloadCv"
          />
        </div>
        <aside class="hidden lg:block">
          <div class="sticky top-4">
            <CandidateScoreCard
              :overall-score="candidate.matchScore"
              :prescanning-score="prescanningScore"
              :interview-score="interviewScore"
              :cv-match-score="candidate.matchScore"
            />
          </div>
        </aside>
      </div>
    </template>
  </div>
</template>
