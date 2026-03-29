<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import { useCandidateStore } from '../stores/candidate.store'
import { useInterviewData } from '../composables/useInterviewData'
import CandidateOverview from '../components/CandidateOverview.vue'
import CvDataView from '../components/CvDataView.vue'
import MatchScoreView from '../components/MatchScoreView.vue'
import HRNotesPanel from '../components/HRNotesPanel.vue'
import CandidateActions from '../components/CandidateActions.vue'
import MessageThread from '../components/MessageThread.vue'
import InterviewReviewPanel from '../components/InterviewReviewPanel.vue'
import { candidateService } from '../services/candidate.service'
import type { ApplicationStatus } from '../types/candidate.types'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const candidateStore = useCandidateStore()
const { prescanningScore, interviewScore, aiSummary, aiSummaryTranslations, aiSummaryInterviewId, fetchInterviewData } = useInterviewData()

const candidateId = computed(() => route.params.id as string)
const candidate = computed(() => candidateStore.currentCandidate)
const hasInterview = computed(() => candidate.value?.interviewEnabled ?? false)

const tabNames = computed(() => {
  const base = ['overview', 'cv', 'prescanning']
  if (hasInterview.value) base.push('interview')
  base.push('analysis', 'notes', 'messages')
  return base
})
const activeTab = computed({
  get: () => { const idx = tabNames.value.indexOf(route.query.tab as string); return idx >= 0 ? idx : 0 },
  set: (val: number) => { router.replace({ query: { ...route.query, tab: tabNames.value[val] } }) },
})

onMounted(async () => {
  await candidateStore.fetchCandidateDetail(candidateId.value)
  await fetchInterviewData(candidateId.value, candidate.value?.interviewEnabled ?? false)
})

async function handleStatusChange(status: ApplicationStatus): Promise<void> { await candidateStore.updateStatus(candidateId.value, status).catch(() => {}) }
async function handleSaveNotes(note: string): Promise<void> { await candidateStore.addNote(candidateId.value, note).catch(() => {}) }
async function handleDownloadCv(): Promise<void> {
  if (!candidate.value?.cvFile) return
  try { const { url } = await candidateService.getCvDownloadUrl(candidateId.value); window.open(url, '_blank') }
  catch { window.open(candidate.value.cvFile, '_blank') }
}
function handleOpenMessages(): void { router.replace({ query: { ...route.query, tab: 'messages' } }) }
function formatScore(score: number | null | undefined): string { return score === null || score === undefined ? '' : String(Math.round(score)) }
</script>

<template>
  <div class="space-y-3 sm:space-y-4">
    <div class="flex items-center gap-2 sm:gap-3">
      <button class="shrink-0 rounded-lg p-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-700" @click="router.back()"><i class="pi pi-arrow-left"></i></button>
      <div class="min-w-0 flex-1">
        <h1 class="truncate text-base font-bold sm:text-lg md:text-2xl">{{ candidate?.candidateName ?? t('common.loading') }}</h1>
        <p v-if="candidate" class="truncate text-xs text-gray-500 sm:text-sm">{{ candidate.vacancyTitle }}</p>
      </div>
    </div>

    <p v-if="candidateStore.error" class="text-sm text-red-600">{{ candidateStore.error }}</p>
    <div v-if="!candidate && candidateStore.loading" class="py-12 text-center"><i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i></div>

    <template v-else-if="candidate">
      <CandidateActions :candidate-id="candidate.id" :candidate-name="candidate.candidateName" :candidate-email="candidate.candidateEmail" :vacancy-id="candidate.vacancyId" :current-status="candidate.status" :loading="candidateStore.loading" @status-change="handleStatusChange" @open-messages="handleOpenMessages" />

      <TabView v-model:activeIndex="activeTab" scrollable>
        <TabPanel value="0">
          <template #header><span class="text-xs sm:text-sm">{{ t('candidates.overview') }}</span></template>
          <div class="py-3 sm:py-4"><CandidateOverview :candidate="candidate" :loading="candidateStore.loading" :prescanning-score="prescanningScore" :interview-score="interviewScore" :ai-summary="aiSummary" :ai-summary-translations="aiSummaryTranslations" :ai-summary-interview-id="aiSummaryInterviewId ?? undefined" /></div>
        </TabPanel>

        <TabPanel value="1">
          <template #header>
            <span class="text-xs sm:text-sm">{{ t('candidates.cv') }}</span>
            <span v-if="candidate.matchScore !== null" class="ml-1.5 inline-flex h-4 min-w-4 items-center justify-center rounded-full px-1 text-[9px] font-bold text-white sm:h-5 sm:min-w-5 sm:px-1.5 sm:text-[10px]" :class="candidate.matchScore >= 70 ? 'bg-green-500' : candidate.matchScore >= 40 ? 'bg-yellow-500' : 'bg-red-500'">{{ formatScore(candidate.matchScore) }}%</span>
          </template>
          <div class="py-3 sm:py-4"><CvDataView :data="candidate.cvParsedData as Record<string, unknown>" :cv-file="candidate.cvFile" :cv-filename="candidate.cvOriginalFilename" :match-score="candidate.matchScore" :match-details="candidate.matchDetails" :match-notes-translations="candidate.matchNotesTranslations" :cv-summary-translations="candidate.cvSummaryTranslations" :application-id="candidate.id" @download-cv="handleDownloadCv" /></div>
        </TabPanel>

        <TabPanel value="2">
          <template #header>
            <span class="text-xs sm:text-sm">{{ t('candidates.prescanning') }}</span>
            <span v-if="prescanningScore !== null" class="ml-1.5 inline-flex h-4 min-w-4 items-center justify-center rounded-full px-1 text-[9px] font-bold text-white sm:h-5 sm:min-w-5 sm:px-1.5 sm:text-[10px]" :class="prescanningScore >= 7 ? 'bg-green-500' : prescanningScore >= 5 ? 'bg-yellow-500' : 'bg-red-500'">{{ formatScore(prescanningScore) }}/10</span>
          </template>
          <div class="py-3 sm:py-4"><InterviewReviewPanel :candidate-id="candidate.id" session-type="prescanning" /></div>
        </TabPanel>

        <TabPanel v-if="hasInterview" value="3">
          <template #header>
            <span class="text-xs sm:text-sm">{{ t('candidates.interview') }}</span>
            <span v-if="interviewScore !== null" class="ml-1.5 inline-flex h-4 min-w-4 items-center justify-center rounded-full px-1 text-[9px] font-bold text-white sm:h-5 sm:min-w-5 sm:px-1.5 sm:text-[10px]" :class="interviewScore >= 7 ? 'bg-green-500' : interviewScore >= 5 ? 'bg-yellow-500' : 'bg-red-500'">{{ formatScore(interviewScore) }}/10</span>
          </template>
          <div class="py-3 sm:py-4"><InterviewReviewPanel :candidate-id="candidate.id" session-type="interview" /></div>
        </TabPanel>

        <TabPanel :value="String(hasInterview ? 4 : 3)">
          <template #header><span class="text-xs sm:text-sm">{{ t('candidates.analysis') }}</span></template>
          <div class="py-3 sm:py-4"><MatchScoreView :overall-score="candidate.matchScore" :match-details="candidate.matchDetails" :match-notes-translations="candidate.matchNotesTranslations" :application-id="candidate.id" :prescanning-score="prescanningScore" :interview-score="interviewScore" /></div>
        </TabPanel>

        <TabPanel :value="String(hasInterview ? 5 : 4)">
          <template #header><span class="text-xs sm:text-sm">{{ t('candidates.notes') }}</span></template>
          <div class="py-3 sm:py-4"><HRNotesPanel :notes="candidate.hrNotes" :loading="candidateStore.loading" @save="handleSaveNotes" /></div>
        </TabPanel>

        <TabPanel :value="String(hasInterview ? 6 : 5)">
          <template #header><span class="text-xs sm:text-sm">{{ t('candidates.messages') }}</span></template>
          <div class="py-3 sm:py-4"><MessageThread :candidate-id="candidate.id" /></div>
        </TabPanel>
      </TabView>
    </template>
  </div>
</template>
