<script setup lang="ts">
import { computed, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import VoiceMessageBubble from '@/features/interviews/components/VoiceMessageBubble.vue'
import InterviewTranscriptQuality from './InterviewTranscriptQuality.vue'

interface ConversationMessage {
  role: 'ai' | 'candidate'
  text: string
  timestamp?: string | number | null
  messageType?: 'text' | 'voice'
  duration?: number
}

const props = defineProps<{
  messages: ConversationMessage[]
  audioBlobUrls: Record<number, string>
  searchQuery: string
  canSeekRecording?: boolean
}>()

const emit = defineEmits<{
  'update:searchQuery': [value: string]
  seekRecording: [seconds: number]
}>()

const { t } = useI18n()

const searchTerms = computed(() =>
  props.searchQuery
    .trim()
    .split(/\s+/)
    .map((term) => term.toLowerCase())
    .filter(Boolean),
)
const visibleMessages = computed(() => {
  const indexedMessages = props.messages.map((message, index) => ({ message, index }))
  if (!searchTerms.value.length) return indexedMessages
  return indexedMessages.filter(({ message }) =>
    searchTerms.value.some((term) => message.text.toLowerCase().includes(term)),
  )
})
const conversationCount = computed(() => visibleMessages.value.length)

function formatTimestamp(ts: string | number | null | undefined): string {
  if (ts === null || ts === undefined || ts === '') return ''
  if (typeof ts === 'number') {
    const mins = Math.floor(ts / 60)
    const secs = Math.floor(ts % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }
  const date = new Date(ts)
  return Number.isNaN(date.getTime())
    ? ''
    : date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function highlightedParts(text: string): Array<{ text: string; match: boolean }> {
  if (!searchTerms.value.length) return [{ text, match: false }]
  const pattern = new RegExp(`(${searchTerms.value.map(escapeRegExp).join('|')})`, 'gi')
  return text.split(pattern).map((part) => ({
    text: part,
    match: searchTerms.value.includes(part.toLowerCase()),
  }))
}

function searchResultsLabel(): string {
  const translated = t('interviews.searchResults', { count: conversationCount.value })
  return translated === 'interviews.searchResults'
    ? `${conversationCount.value} matching messages`
    : translated
}

function canSeek(timestamp: string | number | null | undefined): timestamp is number {
  return props.canSeekRecording === true && typeof timestamp === 'number'
}

onBeforeUnmount(() => {
  Object.values(props.audioBlobUrls).forEach((url) => URL.revokeObjectURL(url))
})
</script>

<template>
  <div class="space-y-3">
    <InterviewTranscriptQuality :messages="messages" />
    <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
      <span class="relative min-w-0 flex-1">
        <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-xs text-gray-400"></i>
        <InputText
          :model-value="searchQuery"
          class="w-full pl-9 text-sm"
          :placeholder="t('interviews.searchConversation', 'Search conversation...')"
          @update:model-value="emit('update:searchQuery', String($event || ''))"
        />
      </span>
      <button
        v-if="searchQuery"
        class="shrink-0 rounded-lg px-3 py-2 text-xs font-medium text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700 dark:hover:bg-gray-800"
        type="button"
        @click="emit('update:searchQuery', '')"
      >
        {{ t('common.clear', 'Clear') }}
      </button>
    </div>
    <p v-if="searchQuery" class="text-xs text-gray-500">{{ searchResultsLabel() }}</p>
    <div v-if="!conversationCount" class="py-4 text-center text-sm text-gray-400">
      {{ t('interviews.noConversation') }}
    </div>
    <div
      v-for="{ message: msg, index: messageIndex } in visibleMessages"
      :key="messageIndex"
      class="flex gap-3"
      :class="msg.role === 'ai' ? '' : 'flex-row-reverse'"
    >
      <div
        class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white"
        :class="msg.role === 'ai' ? 'bg-[color:var(--color-accent)]' : 'bg-gray-500'"
      >
        {{ msg.role === 'ai' ? 'AI' : 'C' }}
      </div>
      <div
        class="max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed"
        :class="
          msg.role === 'ai'
            ? 'rounded-tl-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800'
            : 'rounded-tr-md bg-[color:var(--color-accent)] text-white'
        "
      >
        <template v-if="msg.messageType === 'voice'">
          <div class="mb-1 flex items-center gap-1 text-[10px] opacity-70">
            <i class="pi pi-microphone"></i> {{ t('interviews.voiceMessage') }}
          </div>
          <VoiceMessageBubble
            :audio-url="audioBlobUrls[messageIndex] || ''"
            :duration="msg.duration || 0"
            :transcript="msg.text"
          />
        </template>
        <template v-else>
          <p class="whitespace-pre-wrap">
            <template v-for="(part, partIdx) in highlightedParts(msg.text)" :key="partIdx">
              <mark v-if="part.match" class="rounded bg-yellow-200 px-0.5 text-gray-900">{{
                part.text
              }}</mark>
              <template v-else>{{ part.text }}</template>
            </template>
          </p>
        </template>
        <button
          v-if="canSeek(msg.timestamp)"
          class="mt-1 text-[10px] opacity-70 underline-offset-2 hover:underline"
          type="button"
          @click="emit('seekRecording', msg.timestamp)"
        >
          {{ formatTimestamp(msg.timestamp) }}
        </button>
        <p v-else-if="formatTimestamp(msg.timestamp)" class="mt-1 text-[10px] opacity-50">
          {{ formatTimestamp(msg.timestamp) }}
        </p>
      </div>
    </div>
  </div>
</template>
