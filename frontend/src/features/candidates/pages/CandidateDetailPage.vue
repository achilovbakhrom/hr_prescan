<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import { useCandidateStore } from '../stores/candidate.store'
import { useInterviewStore } from '@/features/interviews/stores/interview.store'
import CandidateOverview from '../components/CandidateOverview.vue'
import CvDataView from '../components/CvDataView.vue'
import MatchScoreView from '../components/MatchScoreView.vue'
import HRNotesPanel from '../components/HRNotesPanel.vue'
import ScheduleForm from '@/features/interviews/components/ScheduleForm.vue'
import InterviewStatusBadge from '@/features/interviews/components/InterviewStatusBadge.vue'
import type { ApplicationStatus } from '../types/candidate.types'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const route = useRoute()
const router = useRouter()
const candidateStore = useCandidateStore()
const interviewStore = useInterviewStore()
const candidateId = computed(() => route.params.id as string)
const candidate = computed(() => candidateStore.currentCandidate)

const showScheduleDialog = ref(false)

const canSchedule = computed(
  () => candidate.value?.status === 'applied',
)

const hasInterview = computed(
  () =>
    candidate.value?.status === 'interview_scheduled' ||
    candidate.value?.status === 'interview_in_progress' ||
    candidate.value?.status === 'interview_completed',
)

onMounted(() => candidateStore.fetchCandidateDetail(candidateId.value))

async function handleStatusChange(status: ApplicationStatus): Promise<void> {
  await candidateStore.updateStatus(candidateId.value, status).catch(() => {})
}

async function handleSaveNotes(note: string): Promise<void> {
  await candidateStore.addNote(candidateId.value, note).catch(() => {})
}

function handleDownloadCv(): void {
  if (candidate.value?.cvFile) {
    window.open(candidate.value.cvFile, '_blank')
  }
}

async function handleScheduleInterview(scheduledAt: string): Promise<void> {
  try {
    const interview = await interviewStore.scheduleInterview(
      candidateId.value,
      { scheduledAt },
    )
    showScheduleDialog.value = false
    router.push({
      name: ROUTE_NAMES.INTERVIEW_DETAIL,
      params: { id: interview.id },
    })
  } catch {
    // error is set in store
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button
          class="text-gray-500 hover:text-gray-700"
          @click="router.back()"
        >
          <i class="pi pi-arrow-left text-lg"></i>
        </button>
        <h1 class="text-2xl font-bold">
          {{ candidate?.candidateName ?? 'Loading...' }}
        </h1>
      </div>
      <Button
        v-if="canSchedule"
        label="Schedule Interview"
        icon="pi pi-calendar-plus"
        size="small"
        @click="showScheduleDialog = true"
      />
    </div>

    <div
      v-if="hasInterview && candidate"
      class="flex items-center gap-3 rounded-lg border border-blue-100 bg-blue-50 px-4 py-3"
    >
      <i class="pi pi-calendar text-blue-600"></i>
      <span class="text-sm text-blue-800">
        Interview status:
      </span>
      <InterviewStatusBadge :status="candidate.status === 'interview_scheduled' ? 'scheduled' : candidate.status === 'interview_in_progress' ? 'in_progress' : 'completed'" />
    </div>

    <p v-if="candidateStore.error" class="text-sm text-red-600">
      {{ candidateStore.error }}
    </p>

    <div v-if="!candidate && candidateStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <template v-else-if="candidate">
      <TabView>
        <TabPanel header="Overview">
          <div class="py-4">
            <CandidateOverview
              :candidate="candidate"
              :loading="candidateStore.loading"
              @status-change="handleStatusChange"
              @download-cv="handleDownloadCv"
            />
          </div>
        </TabPanel>
        <TabPanel header="CV Data">
          <div class="py-4">
            <CvDataView :data="candidate.cvParsedData" />
          </div>
        </TabPanel>
        <TabPanel header="Match Analysis">
          <div class="py-4">
            <MatchScoreView
              :overall-score="candidate.matchScore"
              :match-details="candidate.matchDetails"
            />
          </div>
        </TabPanel>
        <TabPanel header="Notes">
          <div class="py-4">
            <HRNotesPanel
              :notes="candidate.hrNotes"
              :loading="candidateStore.loading"
              @save="handleSaveNotes"
            />
          </div>
        </TabPanel>
      </TabView>
    </template>

    <Dialog
      v-model:visible="showScheduleDialog"
      header="Schedule Interview"
      modal
      class="w-full max-w-md"
    >
      <ScheduleForm
        :loading="interviewStore.loading"
        @submit="handleScheduleInterview"
      />
      <p v-if="interviewStore.error" class="mt-2 text-sm text-red-600">
        {{ interviewStore.error }}
      </p>
    </Dialog>
  </div>
</template>
