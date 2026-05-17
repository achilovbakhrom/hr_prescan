<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import InterviewConversationSection from './InterviewConversationSection.vue'
import InterviewRecordingSection from './InterviewRecordingSection.vue'
import InterviewReviewToolbar from './InterviewReviewToolbar.vue'
import InterviewScoresSection from './InterviewScoresSection.vue'
import { exportTranscriptDoc, exportTranscriptTxt } from '../utils/interviewExport'
import type { PublicCandidateReviewSession } from '../services/candidate.service'

type Section = 'conversation' | 'recording' | 'scores'

const props = defineProps<{
  session: PublicCandidateReviewSession
}>()

const activeSection = ref<Section>('scores')
const conversationSearch = ref('')
const recordingSection = ref<InstanceType<typeof InterviewRecordingSection> | null>(null)

const conversationMessages = computed(() => {
  if (props.session.sessionType === 'prescanning' && props.session.chatHistory?.length) {
    return props.session.chatHistory
  }
  return (props.session.transcript || []).map((entry) => ({
    role: isAiSpeaker(entry) ? ('ai' as const) : ('candidate' as const),
    text: entry.text,
    timestamp: entry.timestamp,
  }))
})

function isAiSpeaker(entry: { speaker?: string; role?: string }): boolean {
  const speaker = (entry.speaker || entry.role || '').toLowerCase()
  return speaker === 'ai' || speaker === 'interviewer'
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
  if (format === 'doc') exportTranscriptDoc(props.session, conversationMessages.value)
  else exportTranscriptTxt(props.session, conversationMessages.value)
}
</script>

<template>
  <div>
    <div class="mb-3 flex items-center justify-between gap-3">
      <div>
        <p class="text-xs font-semibold uppercase tracking-wide text-blue-600">
          {{ session.sessionType }}
        </p>
        <p class="text-sm text-gray-500">{{ session.screeningMode }} · {{ session.status }}</p>
      </div>
      <p v-if="session.overallScore !== null" class="text-lg font-bold text-gray-800">
        {{ session.overallScore }}/10
      </p>
    </div>

    <InterviewReviewToolbar
      v-model:active-section="activeSection"
      :conversation-count="conversationMessages.length"
      :has-recording="Boolean(session.recordingPath)"
      @export="handleExport"
    />

    <InterviewScoresSection
      v-if="activeSection === 'scores'"
      :overall-score="session.overallScore"
      :ai-summary="session.aiSummary"
      :ai-summary-translations="session.aiSummaryTranslations"
      :decision-support="session.decisionSupport"
      :interview-id="session.id"
      :scores="session.scores"
      @find-evidence="handleFindEvidence"
    />

    <InterviewConversationSection
      v-if="activeSection === 'conversation'"
      :messages="conversationMessages"
      :audio-blob-urls="{}"
      :can-seek-recording="Boolean(session.recordingPath)"
      v-model:search-query="conversationSearch"
      @seek-recording="handleSeekRecording"
    />

    <InterviewRecordingSection
      v-if="activeSection === 'recording' && session.recordingPath"
      ref="recordingSection"
      :recording-url="session.recordingPath"
    />
  </div>
</template>
