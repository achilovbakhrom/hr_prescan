<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import { useInterviewStore } from '../stores/interview.store'
import InterviewStatusBadge from '../components/InterviewStatusBadge.vue'
import InterviewScoresView from '../components/InterviewScoresView.vue'
import TranscriptView from '../components/TranscriptView.vue'
import IntegrityFlagsView from '../components/IntegrityFlagsView.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const interviewStore = useInterviewStore()

const TAB_NAMES = ['scores', 'transcript', 'integrity', 'recording'] as const
const activeTab = computed({
  get: () => {
    const tab = route.query.tab as string
    const idx = TAB_NAMES.indexOf(tab as typeof TAB_NAMES[number])
    return idx >= 0 ? idx : 0
  },
  set: (val: number) => {
    router.replace({ query: { ...route.query, tab: TAB_NAMES[val] } })
  },
})

const interviewId = computed(() => route.params.id as string)
const interview = computed(() => interviewStore.currentInterview)

const isScheduled = computed(() => interview.value?.status === 'pending')
const isInProgress = computed(() => interview.value?.status === 'in_progress')
const roomUrl = computed(() => {
  if (!interview.value) return ''
  return `${window.location.origin}/interview/${interview.value.id}/room`
})

onMounted(() => interviewStore.fetchInterviewDetail(interviewId.value))

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}

async function handleCancel(): Promise<void> {
  await interviewStore.cancelInterview(interviewId.value).catch(() => {})
}

async function handleWatchLive(): Promise<void> {
  try {
    const token = await interviewStore.getObserverToken(interviewId.value)
    window.alert(`Observer token: ${token}\n\nLiveKit integration coming in Phase 7.`)
  } catch {
    // error is set in store
  }
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
      <h1 class="text-lg font-bold md:text-2xl">{{ t('interviews.detailPage.title') }}</h1>
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
      <div class="rounded-lg border border-gray-200 bg-white p-4 md:p-6">
        <div class="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-start sm:justify-between sm:gap-4">
          <div class="space-y-1">
            <p class="text-base font-semibold md:text-lg">{{ interview.candidateName }}</p>
            <p class="text-sm text-gray-600">{{ interview.vacancyTitle }}</p>
            <p class="text-xs text-gray-500 sm:text-sm">
              {{ formatDate(interview.createdAt) }} &middot;
              {{ interview.durationMinutes }} min
            </p>
          </div>
          <div class="flex flex-wrap items-center gap-2 sm:gap-3">
            <Tag
              :value="interview.sessionType === 'prescanning' ? t('candidates.prescanning') : t('candidates.interview')"
              :severity="interview.sessionType === 'prescanning' ? 'info' : 'success'"
            />
            <InterviewStatusBadge :status="interview.status" />
            <Button
              v-if="isScheduled || isInProgress"
              :label="t('interviews.detailPage.openRoom')"
              icon="pi pi-external-link"
              size="small"
              severity="info"
              @click="router.push(`/interview/${interview.id}/room`)"
            />
            <Button
              v-if="isScheduled"
              :label="t('common.cancel')"
              severity="danger"
              size="small"
              outlined
              :loading="interviewStore.loading"
              @click="handleCancel"
            />
            <Button
              v-if="isInProgress"
              :label="t('interviews.detailPage.watchLive')"
              icon="pi pi-eye"
              size="small"
              @click="handleWatchLive"
            />
          </div>
        </div>
        <div v-if="isScheduled || isInProgress" class="mt-4 rounded border border-blue-100 bg-blue-50 p-3">
          <p class="text-sm font-medium text-blue-800">{{ t('interviews.detailPage.roomLink') }}</p>
          <p class="mt-1 text-sm text-blue-600">
            {{ roomUrl }}
          </p>
          <p class="mt-1 text-xs text-blue-500">{{ t('interviews.detailPage.roomLinkHint') }}</p>
        </div>
        <p
          v-if="interview.aiSummary"
          class="mt-4 rounded bg-gray-50 p-3 text-sm text-gray-700"
        >
          {{ interview.aiSummary }}
        </p>
      </div>

      <TabView v-model:activeIndex="activeTab">
        <TabPanel value="0" :header="t('interviews.detailPage.tabScores')">
          <div class="py-4">
            <InterviewScoresView :scores="interview.scores" />
          </div>
        </TabPanel>
        <TabPanel value="1" :header="t('interviews.detailPage.tabTranscript')">
          <div class="py-4">
            <TranscriptView :transcript="interview.transcript" />
          </div>
        </TabPanel>
        <TabPanel value="2" :header="t('interviews.detailPage.tabIntegrity')">
          <div class="py-4">
            <IntegrityFlagsView :flags="interview.integrityFlags" />
          </div>
        </TabPanel>
        <TabPanel value="3" :header="t('interviews.detailPage.tabRecording')">
          <div class="py-4">
            <div
              v-if="interview.recordingPath"
              class="rounded-lg border border-gray-200 p-6"
            >
              <p class="mb-2 text-sm font-medium text-gray-700">
                {{ t('interviews.detailPage.recordingPath') }}
              </p>
              <code class="text-sm text-gray-600">
                {{ interview.recordingPath }}
              </code>
              <p class="mt-4 text-xs text-gray-400">
                {{ t('interviews.detailPage.playbackNote') }}
              </p>
            </div>
            <p v-else class="text-sm text-gray-500">
              {{ t('interviews.detailPage.noRecording') }}
            </p>
          </div>
        </TabPanel>
      </TabView>
    </template>
  </div>
</template>
