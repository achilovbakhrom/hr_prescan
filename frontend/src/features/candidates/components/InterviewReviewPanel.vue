<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiClient } from '@/shared/api/client'
import { candidateService } from '../services/candidate.service'
import InterviewScoresSection from './InterviewScoresSection.vue'
import VoiceMessageBubble from '@/features/interviews/components/VoiceMessageBubble.vue'

const props = defineProps<{
  candidateId: string
  sessionType?: string
}>()

interface ChatMessage {
  role: 'ai' | 'candidate'
  text: string
  timestamp: string
  messageType?: 'text' | 'voice'
  audioUrl?: string
  duration?: number
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
  overallScore: number | null
  aiSummary: string
  aiSummaryTranslations: Record<string, string>
  chatHistory: ChatMessage[]
  scores: InterviewScore[]
  createdAt: string
}

const { t } = useI18n()

const interview = ref<InterviewData | null>(null)
const loading = ref(false)
const error = ref('')
const activeSection = ref<'conversation' | 'scores'>('scores')
const audioBlobUrls = ref<Record<number, string>>({})

function formatTime(ts: string): string {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
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

onMounted(async () => {
  loading.value = true
  try {
    const data = (await candidateService.getCandidateInterview(
      props.candidateId,
      props.sessionType,
    )) as unknown as InterviewData
    interview.value = data
    if (data.chatHistory)
      data.chatHistory.forEach((msg: ChatMessage, idx: number) => {
        if (msg.messageType === 'voice') loadAudioBlob(idx)
      })
  } catch {
    error.value = 'Interview data not available yet.'
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  Object.values(audioBlobUrls.value).forEach((url) => URL.revokeObjectURL(url))
})
</script>

<template>
  <div>
    <div v-if="loading" class="py-8 text-center">
      <i class="pi pi-spinner pi-spin text-2xl text-gray-400"></i>
    </div>
    <div v-else-if="error" class="py-8 text-center text-sm text-gray-400">{{ error }}</div>

    <template v-else-if="interview">
      <div class="mb-4 flex gap-2">
        <button
          class="rounded-lg px-4 py-2 text-sm font-medium transition-colors"
          :class="
            activeSection === 'scores'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-600 dark:text-gray-400 hover:bg-gray-200'
          "
          @click="activeSection = 'scores'"
        >
          {{ t('interviews.scores') }}
        </button>
        <button
          class="rounded-lg px-4 py-2 text-sm font-medium transition-colors"
          :class="
            activeSection === 'conversation'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-600 dark:text-gray-400 hover:bg-gray-200'
          "
          @click="activeSection = 'conversation'"
        >
          {{ t('interviews.conversation') }} ({{ interview.chatHistory?.length || 0 }}
          {{ t('interviews.messages') }})
        </button>
      </div>

      <InterviewScoresSection
        v-if="activeSection === 'scores'"
        :overall-score="interview.overallScore"
        :ai-summary="interview.aiSummary"
        :ai-summary-translations="interview.aiSummaryTranslations"
        :interview-id="interview.id"
        :scores="interview.scores"
        @update:ai-summary-translations="
          (tr) => {
            if (interview) interview.aiSummaryTranslations = tr
          }
        "
      />

      <div v-if="activeSection === 'conversation'" class="space-y-3">
        <div v-if="!interview.chatHistory?.length" class="py-4 text-center text-sm text-gray-400">
          {{ t('interviews.noConversation') }}
        </div>
        <div
          v-for="(msg, idx) in interview.chatHistory"
          :key="idx"
          class="flex gap-3"
          :class="msg.role === 'ai' ? '' : 'flex-row-reverse'"
        >
          <div
            class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white"
            :class="msg.role === 'ai' ? 'bg-blue-500' : 'bg-gray-500'"
          >
            {{ msg.role === 'ai' ? 'AI' : 'C' }}
          </div>
          <div
            class="max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed"
            :class="
              msg.role === 'ai'
                ? 'rounded-tl-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800'
                : 'rounded-tr-md bg-blue-600 dark:bg-blue-700 text-white'
            "
          >
            <template v-if="msg.messageType === 'voice'">
              <div class="mb-1 flex items-center gap-1 text-[10px] opacity-70">
                <i class="pi pi-microphone"></i> {{ t('interviews.voiceMessage') }}
              </div>
              <VoiceMessageBubble
                :audio-url="audioBlobUrls[idx] || ''"
                :duration="msg.duration || 0"
                :transcript="msg.text"
              />
            </template>
            <template v-else
              ><p class="whitespace-pre-wrap">{{ msg.text }}</p></template
            >
            <p class="mt-1 text-[10px] opacity-50">{{ formatTime(msg.timestamp) }}</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
