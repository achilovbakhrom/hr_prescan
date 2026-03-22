<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import ProgressBar from 'primevue/progressbar'
import { apiClient } from '@/shared/api/client'
import { candidateService } from '../services/candidate.service'
import VoiceMessageBubble from '@/features/interviews/components/VoiceMessageBubble.vue'

const { t } = useI18n()

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
  score: number
  aiNotes: string
}

interface InterviewData {
  id: string
  status: string
  overallScore: number | null
  aiSummary: string
  chatHistory: ChatMessage[]
  scores: InterviewScore[]
  createdAt: string
}

const interview = ref<InterviewData | null>(null)
const loading = ref(false)
const error = ref('')
const activeSection = ref<'conversation' | 'scores'>('scores')

function scoreColor(score: number): string {
  if (score >= 8) return 'text-green-600'
  if (score >= 6) return 'text-blue-600'
  if (score >= 4) return 'text-yellow-600'
  return 'text-red-600'
}

function scoreBg(score: number): string {
  if (score >= 8) return 'bg-green-500'
  if (score >= 6) return 'bg-blue-500'
  if (score >= 4) return 'bg-yellow-500'
  return 'bg-red-500'
}

function formatTime(ts: string): string {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const audioBlobUrls = ref<Record<number, string>>({})

async function loadAudioBlob(messageIndex: number): Promise<void> {
  if (!interview.value || audioBlobUrls.value[messageIndex]) return
  try {
    const response = await apiClient.get(
      `/hr/interviews/${interview.value.id}/voice/${messageIndex}/audio/`,
      { responseType: 'blob' }
    )
    audioBlobUrls.value[messageIndex] = URL.createObjectURL(response.data as Blob)
  } catch {
    // Audio not available
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const data = await candidateService.getCandidateInterview(props.candidateId, props.sessionType) as unknown as InterviewData
    interview.value = data

    if (data.chatHistory) {
      data.chatHistory.forEach((msg: ChatMessage, idx: number) => {
        if (msg.messageType === 'voice') {
          loadAudioBlob(idx)
        }
      })
    }
  } catch {
    error.value = 'Interview data not available yet.'
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  Object.values(audioBlobUrls.value).forEach(url => URL.revokeObjectURL(url))
})
</script>

<template>
  <div>
    <div v-if="loading" class="py-8 text-center">
      <i class="pi pi-spinner pi-spin text-2xl text-gray-400"></i>
    </div>

    <div v-else-if="error" class="py-8 text-center text-sm text-gray-400">
      {{ error }}
    </div>

    <template v-else-if="interview">
      <!-- Section Toggle -->
      <div class="mb-4 flex gap-2">
        <button
          class="rounded-lg px-4 py-2 text-sm font-medium transition-colors"
          :class="activeSection === 'scores' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
          @click="activeSection = 'scores'"
        >
          {{ t('interviews.scores') }}
        </button>
        <button
          class="rounded-lg px-4 py-2 text-sm font-medium transition-colors"
          :class="activeSection === 'conversation' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
          @click="activeSection = 'conversation'"
        >
          {{ t('interviews.conversation') }} ({{ interview.chatHistory?.length || 0 }} {{ t('interviews.messages') }})
        </button>
      </div>

      <!-- Scores Section -->
      <div v-if="activeSection === 'scores'">
        <!-- Overall Score -->
        <div v-if="interview.overallScore !== null" class="mb-4 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 p-5">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-medium text-blue-600 uppercase tracking-wide">{{ t('interviews.overallScore') }}</p>
              <p class="mt-1 text-4xl font-bold" :class="scoreColor(interview.overallScore)">
                {{ interview.overallScore }}<span class="text-lg text-gray-400">/10</span>
              </p>
            </div>
            <div class="h-16 w-16 rounded-full border-4 flex items-center justify-center" :class="scoreBg(interview.overallScore) + ' border-opacity-20'">
              <span class="text-xl font-bold text-white">{{ Math.round(interview.overallScore) }}</span>
            </div>
          </div>
        </div>

        <!-- AI Summary -->
        <div v-if="interview.aiSummary" class="mb-4 rounded-lg border border-gray-200 bg-gray-50 p-4">
          <p class="mb-1 text-xs font-semibold text-gray-500 uppercase tracking-wide">{{ t('interviews.aiAssessment') }}</p>
          <p class="text-sm text-gray-700 leading-relaxed">{{ interview.aiSummary }}</p>
        </div>

        <!-- Per-criteria scores -->
        <div v-if="interview.scores?.length" class="space-y-3">
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">{{ t('interviews.criteriaBreakdown') }}</p>
          <div
            v-for="score in interview.scores"
            :key="score.id"
            class="rounded-lg border border-gray-200 p-3"
          >
            <div class="mb-1.5 flex items-center justify-between">
              <span class="text-sm font-medium text-gray-700">{{ score.criteriaName }}</span>
              <span class="text-sm font-bold" :class="scoreColor(score.score)">
                {{ score.score }}/10
              </span>
            </div>
            <ProgressBar :value="score.score * 10" :show-value="false" style="height: 6px" />
            <p v-if="score.aiNotes" class="mt-1.5 text-xs text-gray-500">{{ score.aiNotes }}</p>
          </div>
        </div>

        <p v-else class="py-4 text-center text-sm text-gray-400">
          {{ t('interviews.noScores') }}
        </p>
      </div>

      <!-- Conversation Section -->
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
            :class="msg.role === 'ai' ? 'rounded-tl-md bg-white border border-gray-200 text-gray-800' : 'rounded-tr-md bg-blue-600 text-white'"
          >
            <!-- Voice message -->
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
            <!-- Text message -->
            <template v-else>
              <p class="whitespace-pre-wrap">{{ msg.text }}</p>
            </template>
            <p class="mt-1 text-[10px] opacity-50">{{ formatTime(msg.timestamp) }}</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
