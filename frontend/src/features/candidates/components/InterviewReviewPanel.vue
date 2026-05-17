<script setup lang="ts">
import { computed, nextTick, ref, onMounted } from 'vue'
import { apiClient } from '@/shared/api/client'
import { candidateService } from '../services/candidate.service'
import InterviewConversationSection from './InterviewConversationSection.vue'
import InterviewRecordingSection from './InterviewRecordingSection.vue'
import InterviewReviewToolbar from './InterviewReviewToolbar.vue'
import InterviewScoresSection from './InterviewScoresSection.vue'
import { exportTranscriptDoc, exportTranscriptTxt } from '../utils/interviewExport'
import type { DecisionSupport } from '@/shared/types/interview.types'

const props = defineProps<{
  candidateId: string
  sessionType?: string
}>()

interface ChatMessage {
  role: 'ai' | 'candidate'
  text: string
  timestamp?: string | number | null
  messageType?: 'text' | 'voice'
  audioUrl?: string
  duration?: number
}
interface TranscriptEntry {
  speaker?: string
  role?: string
  text: string
  timestamp?: number | string
}
interface InterviewScore {
  id: string
  criteria: string
  criteriaName: string
  criteriaTranslations?: Record<string, string>
  score: number
  aiNotes: string
  aiNotesTranslations: Record<string, string>
}
interface InterviewData {
  id: string
  status: string
  sessionType: 'prescanning' | 'interview'
  screeningMode: 'chat' | 'meet'
  overallScore: number | null
  aiSummary: string
  aiSummaryTranslations: Record<string, string>
  decisionSupport?: DecisionSupport
  chatHistory: ChatMessage[]
  transcript: TranscriptEntry[]
  recordingPath?: string
  scores: InterviewScore[]
  createdAt: string
}

const interview = ref<InterviewData | null>(null)
const loading = ref(false)
const error = ref('')
const activeSection = ref<'conversation' | 'recording' | 'scores'>('scores')
const audioBlobUrls = ref<Record<number, string>>({})
const conversationSearch = ref('')
const recordingSection = ref<InstanceType<typeof InterviewRecordingSection> | null>(null)

const conversationMessages = computed<ChatMessage[]>(() => {
  if (!interview.value) return []
  if (interview.value.sessionType === 'prescanning' && interview.value.chatHistory?.length) {
    return interview.value.chatHistory
  }
  return (interview.value.transcript || []).map((entry) => ({
    role: isAiSpeaker(entry) ? 'ai' : 'candidate',
    text: entry.text,
    timestamp: entry.timestamp,
  }))
})

function isAiSpeaker(entry: TranscriptEntry): boolean {
  const speaker = (entry.speaker || entry.role || '').toLowerCase()
  return speaker === 'ai' || speaker === 'interviewer'
}

async function loadAudioBlob(messageIndex: number): Promise<void> {
  if (!interview.value || audioBlobUrls.value[messageIndex]) return
  try {
    const response = await apiClient.get(
      `/hr/interviews/${interview.value.id}/voice/${messageIndex}/audio/`,
      { responseType: 'blob' },
    )
    audioBlobUrls.value[messageIndex] = URL.createObjectURL(response.data as Blob)
  } catch {
    /* Audio not available */
  }
}

function handleFindEvidence(query: string): void {
  conversationSearch.value = query
  activeSection.value = 'conversation'
}

async function handleSeekRecording(seconds: number): Promise<void> {
  activeSection.value = 'recording'
  await nextTick()
  recordingSection.value?.seekTo(seconds)
}

function handleExport(format: 'doc' | 'txt'): void {
  if (!interview.value) return
  if (format === 'doc') exportTranscriptDoc(interview.value, conversationMessages.value)
  else exportTranscriptTxt(interview.value, conversationMessages.value)
}

onMounted(async () => {
  loading.value = true
  try {
    const data = (await candidateService.getCandidateInterview(
      props.candidateId,
      props.sessionType,
    )) as unknown as InterviewData
    interview.value = data
    if (data.sessionType === 'prescanning' && data.chatHistory) {
      data.chatHistory.forEach((msg: ChatMessage, idx: number) => {
        if (msg.messageType === 'voice') loadAudioBlob(idx)
      })
    }
  } catch {
    error.value = 'Interview data not available yet.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div v-if="loading" class="py-8 text-center">
      <i class="pi pi-spinner pi-spin text-2xl text-gray-400"></i>
    </div>
    <div v-else-if="error" class="py-8 text-center text-sm text-gray-400">{{ error }}</div>

    <template v-else-if="interview">
      <InterviewReviewToolbar
        v-model:active-section="activeSection"
        :conversation-count="conversationMessages.length"
        :has-recording="Boolean(interview.recordingPath)"
        @export="handleExport"
      />

      <InterviewScoresSection
        v-if="activeSection === 'scores'"
        :overall-score="interview.overallScore"
        :ai-summary="interview.aiSummary"
        :ai-summary-translations="interview.aiSummaryTranslations"
        :decision-support="interview.decisionSupport"
        :interview-id="interview.id"
        :scores="interview.scores"
        @update:ai-summary-translations="
          (tr) => {
            if (interview) interview.aiSummaryTranslations = tr
          }
        "
        @find-evidence="handleFindEvidence"
      />

      <InterviewConversationSection
        v-if="activeSection === 'conversation'"
        :messages="conversationMessages"
        :audio-blob-urls="audioBlobUrls"
        :can-seek-recording="Boolean(interview.recordingPath)"
        v-model:search-query="conversationSearch"
        @seek-recording="handleSeekRecording"
      />

      <InterviewRecordingSection
        v-if="activeSection === 'recording' && interview.recordingPath"
        ref="recordingSection"
        :recording-url="interview.recordingPath"
      />
    </template>
  </div>
</template>
