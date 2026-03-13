<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import { useInterviewStore } from '../stores/interview.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import InterviewStatusBadge from '../components/InterviewStatusBadge.vue'
import InterviewScoresView from '../components/InterviewScoresView.vue'
import TranscriptView from '../components/TranscriptView.vue'
import IntegrityFlagsView from '../components/IntegrityFlagsView.vue'

const route = useRoute()
const router = useRouter()
const interviewStore = useInterviewStore()

const interviewId = computed(() => route.params.id as string)
const interview = computed(() => interviewStore.currentInterview)

const isScheduled = computed(() => interview.value?.status === 'scheduled')
const isInProgress = computed(() => interview.value?.status === 'in_progress')

onMounted(() => interviewStore.fetchInterviewDetail(interviewId.value))

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}

async function handleCancel(): Promise<void> {
  await interviewStore.cancelInterview(interviewId.value).catch(() => {})
}

function handleWatchLive(): void {
  router.push({
    name: ROUTE_NAMES.INTERVIEW_OBSERVE,
    params: { id: interviewId.value },
  })
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <button
        class="text-gray-500 hover:text-gray-700"
        @click="router.back()"
      >
        <i class="pi pi-arrow-left text-lg"></i>
      </button>
      <h1 class="text-2xl font-bold">Interview Details</h1>
    </div>

    <p v-if="interviewStore.error" class="text-sm text-red-600">
      {{ interviewStore.error }}
    </p>

    <div
      v-if="!interview && interviewStore.loading"
      class="py-12 text-center"
    >
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <template v-else-if="interview">
      <div class="rounded-lg border border-gray-200 bg-white p-6">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div class="space-y-1">
            <p class="text-lg font-semibold">{{ interview.candidateName }}</p>
            <p class="text-sm text-gray-600">{{ interview.vacancyTitle }}</p>
            <p class="text-sm text-gray-500">
              {{ formatDate(interview.scheduledAt) }} &middot;
              {{ interview.durationMinutes }} min
            </p>
          </div>
          <div class="flex items-center gap-3">
            <InterviewStatusBadge :status="interview.status" />
            <Button
              v-if="isScheduled"
              label="Cancel"
              severity="danger"
              size="small"
              outlined
              :loading="interviewStore.loading"
              @click="handleCancel"
            />
            <Button
              v-if="isInProgress"
              label="Watch Live"
              icon="pi pi-eye"
              size="small"
              @click="handleWatchLive"
            />
          </div>
        </div>
        <p
          v-if="interview.aiSummary"
          class="mt-4 rounded bg-gray-50 p-3 text-sm text-gray-700"
        >
          {{ interview.aiSummary }}
        </p>
      </div>

      <TabView>
        <TabPanel header="Scores">
          <div class="py-4">
            <InterviewScoresView :scores="interview.scores" />
          </div>
        </TabPanel>
        <TabPanel header="Transcript">
          <div class="py-4">
            <TranscriptView :transcript="interview.transcript" />
          </div>
        </TabPanel>
        <TabPanel header="Integrity">
          <div class="py-4">
            <IntegrityFlagsView :flags="interview.integrityFlags" />
          </div>
        </TabPanel>
        <TabPanel header="Recording">
          <div class="py-4">
            <div
              v-if="interview.recordingPath"
              class="rounded-lg border border-gray-200 p-6"
            >
              <p class="mb-2 text-sm font-medium text-gray-700">
                Recording Path
              </p>
              <code class="text-sm text-gray-600">
                {{ interview.recordingPath }}
              </code>
              <p class="mt-4 text-xs text-gray-400">
                Audio/video playback will be available in a future release.
              </p>
            </div>
            <p v-else class="text-sm text-gray-500">
              No recording available.
            </p>
          </div>
        </TabPanel>
      </TabView>
    </template>
  </div>
</template>
