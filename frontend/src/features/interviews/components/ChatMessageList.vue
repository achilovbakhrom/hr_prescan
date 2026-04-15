<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import VoiceMessageBubble from './VoiceMessageBubble.vue'
import type { ChatMessage } from '../types/interview.types'

defineProps<{
  messages: ChatMessage[]
  isTyping: boolean
  formatTime: (timestamp: string) => string
  getAudioUrl: (index: number) => string
}>()

const { t } = useI18n()
</script>

<template>
  <div class="mx-auto max-w-3xl space-y-4">
    <!-- Date header -->
    <div class="flex items-center justify-center">
      <span class="rounded-full bg-gray-200 px-3 py-1 text-[10px] font-medium text-gray-500">
        {{ t('interviews.chatPage.today') }}
      </span>
    </div>

    <div
      v-for="(msg, idx) in messages"
      :key="idx"
      class="flex"
      :class="msg.role === 'candidate' ? 'justify-end' : 'justify-start'"
    >
      <!-- AI message -->
      <div v-if="msg.role === 'ai'" class="flex max-w-[80%] gap-2.5">
        <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-blue-700 shadow-sm">
          <i class="pi pi-comments text-xs text-white"></i>
        </div>
        <div class="min-w-0">
          <div class="rounded-2xl rounded-tl-sm bg-white px-4 py-3 shadow-sm ring-1 ring-gray-100">
            <p class="whitespace-pre-wrap text-[13px] leading-relaxed text-gray-800">{{ msg.text }}</p>
          </div>
          <span class="mt-1 block pl-1 text-[10px] text-gray-400">{{ formatTime(msg.timestamp) }}</span>
        </div>
      </div>

      <!-- Candidate voice message -->
      <div v-else-if="msg.messageType === 'voice'" class="max-w-[80%]">
        <div class="rounded-2xl rounded-tr-sm bg-blue-600 px-4 py-3 shadow-sm">
          <div v-if="msg.text === 'Transcribing...'" class="flex items-center gap-2 text-white/80">
            <i class="pi pi-spinner pi-spin text-xs"></i>
            <span class="text-[13px]">{{ t('interviews.chat.transcribing') }}</span>
          </div>
          <VoiceMessageBubble
            v-else
            :audio-url="getAudioUrl(idx)"
            :duration="msg.duration || 0"
            :transcript="msg.text"
          />
        </div>
        <span class="mt-1 block pr-1 text-right text-[10px] text-gray-400">
          {{ formatTime(msg.timestamp) }}
          <i class="pi pi-microphone ml-0.5 text-blue-400" style="font-size: 8px"></i>
        </span>
      </div>

      <!-- Candidate text message -->
      <div v-else class="max-w-[80%]">
        <div class="rounded-2xl rounded-tr-sm bg-blue-600 px-4 py-3 shadow-sm">
          <p class="whitespace-pre-wrap text-[13px] leading-relaxed text-white">{{ msg.text }}</p>
        </div>
        <span class="mt-1 block pr-1 text-right text-[10px] text-gray-400">
          {{ formatTime(msg.timestamp) }}
          <i class="pi pi-check-double ml-0.5 text-blue-400" style="font-size: 8px"></i>
        </span>
      </div>
    </div>

    <!-- Typing indicator -->
    <div v-if="isTyping" class="flex justify-start">
      <div class="flex max-w-[80%] gap-2.5">
        <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-blue-700 shadow-sm">
          <i class="pi pi-comments text-xs text-white"></i>
        </div>
        <div class="rounded-2xl rounded-tl-sm bg-white px-5 py-3.5 shadow-sm ring-1 ring-gray-100">
          <div class="flex items-center gap-1.5">
            <span class="typing-dot h-2 w-2 rounded-full bg-gray-400"></span>
            <span class="typing-dot h-2 w-2 rounded-full bg-gray-400" style="animation-delay: 0.15s"></span>
            <span class="typing-dot h-2 w-2 rounded-full bg-gray-400" style="animation-delay: 0.3s"></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

.typing-dot {
  animation: typing 1.4s ease-in-out infinite;
}
</style>
