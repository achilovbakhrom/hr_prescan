<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import { useCandidateStore } from '../stores/candidate.store'
import CandidateOverview from '../components/CandidateOverview.vue'
import CvDataView from '../components/CvDataView.vue'
import MatchScoreView from '../components/MatchScoreView.vue'
import HRNotesPanel from '../components/HRNotesPanel.vue'
import CandidateActions from '../components/CandidateActions.vue'
import MessageThread from '../components/MessageThread.vue'
import InterviewReviewPanel from '../components/InterviewReviewPanel.vue'
import { candidateService } from '../services/candidate.service'
import type { ApplicationStatus } from '../types/candidate.types'

const route = useRoute()
const router = useRouter()
const candidateStore = useCandidateStore()
const TAB_NAMES = ['overview', 'cv', 'interview', 'analysis', 'notes', 'messages'] as const
const activeTab = computed({
  get: () => {
    const tab = route.query.tab as string
    const idx = TAB_NAMES.indexOf(tab as (typeof TAB_NAMES)[number])
    return idx >= 0 ? idx : 0
  },
  set: (val: number) => {
    router.replace({ query: { ...route.query, tab: TAB_NAMES[val] } })
  },
})
const candidateId = computed(() => route.params.id as string)
const candidate = computed(() => candidateStore.currentCandidate)

// Interview score for badge
const interviewScore = ref<number | null>(null)
const aiSummary = ref<string | null>(null)

onMounted(async () => {
  await candidateStore.fetchCandidateDetail(candidateId.value)
  try {
    const data = await candidateService.getCandidateInterview(candidateId.value) as Record<string, unknown>
    interviewScore.value = (data.overallScore as number) ?? null
    aiSummary.value = (data.aiSummary as string) ?? null
  } catch {
    // no interview yet
  }
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

function handleOpenMessages(): void {
  router.replace({ query: { ...route.query, tab: 'messages' } })
}

function formatScore(score: number | null | undefined): string {
  if (score === null || score === undefined) return ''
  return String(Math.round(score))
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <button class="text-gray-500 hover:text-gray-700" @click="router.back()">
        <i class="pi pi-arrow-left text-lg"></i>
      </button>
      <h1 class="text-2xl font-bold">
        {{ candidate?.candidateName ?? 'Loading...' }}
      </h1>
    </div>

    <p v-if="candidateStore.error" class="text-sm text-red-600">
      {{ candidateStore.error }}
    </p>

    <div v-if="!candidate && candidateStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <template v-else-if="candidate">
      <CandidateActions
        :candidate-id="candidate.id"
        :candidate-name="candidate.candidateName"
        :candidate-email="candidate.candidateEmail"
        :vacancy-id="candidate.vacancyId"
        :current-status="candidate.status"
        :loading="candidateStore.loading"
        @status-change="handleStatusChange"
        @open-messages="handleOpenMessages"
      />

      <TabView v-model:activeIndex="activeTab">
        <TabPanel value="0" header="Overview">
          <div class="py-4">
            <CandidateOverview
              :candidate="candidate"
              :loading="candidateStore.loading"
              :interview-score="interviewScore"
              :ai-summary="aiSummary"
            />
          </div>
        </TabPanel>

        <TabPanel value="1">
          <template #header>
            <span>CV Data</span>
            <span
              v-if="candidate.matchScore !== null"
              class="ml-2 inline-flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-[10px] font-bold text-white"
              :class="
                candidate.matchScore >= 70
                  ? 'bg-green-500'
                  : candidate.matchScore >= 40
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
              "
              >{{ formatScore(candidate.matchScore) }}%</span
            >
          </template>
          <div class="py-4">
            <CvDataView
              :data="candidate.cvParsedData as Record<string, unknown>"
              :cv-file="candidate.cvFile"
              :cv-filename="candidate.cvOriginalFilename"
              :match-score="candidate.matchScore"
              :match-details="candidate.matchDetails"
              @download-cv="handleDownloadCv"
            />
          </div>
        </TabPanel>

        <TabPanel value="2">
          <template #header>
            <span>Interview</span>
            <span
              v-if="interviewScore !== null"
              class="ml-2 inline-flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-[10px] font-bold text-white"
              :class="
                interviewScore >= 7
                  ? 'bg-green-500'
                  : interviewScore >= 5
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
              "
              >{{ formatScore(interviewScore) }}/10</span
            >
          </template>
          <div class="py-4">
            <InterviewReviewPanel :candidate-id="candidate.id" />
          </div>
        </TabPanel>

        <TabPanel value="3" header="Analysis">
          <div class="py-4">
            <MatchScoreView
              :overall-score="candidate.matchScore"
              :match-details="candidate.matchDetails"
              :interview-score="interviewScore"
            />
          </div>
        </TabPanel>

        <TabPanel value="4" header="Notes">
          <div class="py-4">
            <HRNotesPanel
              :notes="candidate.hrNotes"
              :loading="candidateStore.loading"
              @save="handleSaveNotes"
            />
          </div>
        </TabPanel>
        <TabPanel value="5" header="Messages">
          <div class="py-4">
            <MessageThread :candidate-id="candidate.id" />
          </div>
        </TabPanel>
      </TabView>
    </template>
  </div>
</template>

<style scoped>
/* Keep white background on panels, remove only side/bottom borders */
:deep(.p-tabview-panels) {
  border-top: none !important;
  background: white !important;
  border-radius: 0 0 0.5rem 0.5rem !important;
}

/* Clean up tab list */
:deep(.p-tabview-tablist) {
  border-width: 0 0 1px 0 !important;
  border-color: #e5e7eb !important;
}

/* Remove bottom border from tab header links */
:deep(.p-tabview-tab-header) {
  border-bottom: none !important;
  border: none !important;
}
</style>
