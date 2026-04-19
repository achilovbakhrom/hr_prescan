<script setup lang="ts">
/**
 * ChatMessageList — renders the interview conversation.
 *
 * T13 redesign: AI messages use glass + violet AI tint; candidate
 * messages are solid surface-raised; typing indicator is 3 pulsing dots.
 */
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
      <span
        class="bg-glass-2 font-mono rounded-full px-3 py-1 text-[10px] font-medium text-[color:var(--color-text-muted)]"
      >
        {{ t('interviews.chatPage.today') }}
      </span>
    </div>

    <div
      v-for="(msg, idx) in messages"
      :key="idx"
      class="flex animate-[msg-in_380ms_var(--ease-ios)_both]"
      :class="msg.role === 'candidate' ? 'justify-end' : 'justify-start'"
    >
      <!-- AI message -->
      <div v-if="msg.role === 'ai'" class="flex max-w-[85%] gap-2.5">
        <div
          class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[color:var(--color-accent-ai-soft)] ring-1 ring-[color:var(--color-accent-ai)]/30"
        >
          <i class="pi pi-sparkles text-xs text-[color:var(--color-accent-ai)]"></i>
        </div>
        <div class="min-w-0">
          <div class="bg-glass-1 border-glass shadow-glass rounded-2xl rounded-tl-sm px-4 py-2.5">
            <p
              class="whitespace-pre-wrap text-[13px] leading-relaxed text-[color:var(--color-text-primary)]"
            >
              {{ msg.text }}
            </p>
          </div>
          <span class="mt-1 block pl-1 font-mono text-[10px] text-[color:var(--color-text-muted)]">
            {{ formatTime(msg.timestamp) }}
          </span>
        </div>
      </div>

      <!-- Candidate voice message -->
      <div v-else-if="msg.messageType === 'voice'" class="max-w-[80%]">
        <div class="rounded-2xl rounded-tr-sm bg-[color:var(--color-accent)] px-4 py-3 shadow-card">
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
        <span
          class="mt-1 block pr-1 text-right font-mono text-[10px] text-[color:var(--color-text-muted)]"
        >
          {{ formatTime(msg.timestamp) }}
          <i
            class="pi pi-microphone ml-0.5 text-[color:var(--color-accent)]"
            style="font-size: 8px"
          ></i>
        </span>
      </div>

      <!-- Candidate text message -->
      <div v-else class="max-w-[80%]">
        <div
          class="rounded-2xl rounded-tr-sm bg-[color:var(--color-surface-raised)] px-4 py-2.5 shadow-card ring-1 ring-[color:var(--color-border-soft)]"
        >
          <p
            class="whitespace-pre-wrap text-[13px] leading-relaxed text-[color:var(--color-text-primary)]"
          >
            {{ msg.text }}
          </p>
        </div>
        <span
          class="mt-1 block pr-1 text-right font-mono text-[10px] text-[color:var(--color-text-muted)]"
        >
          {{ formatTime(msg.timestamp) }}
          <i
            class="pi pi-check-double ml-0.5 text-[color:var(--color-accent)]"
            style="font-size: 8px"
          ></i>
        </span>
      </div>
    </div>

    <!-- Typing indicator -->
    <div v-if="isTyping" class="flex justify-start">
      <div class="flex max-w-[80%] gap-2.5">
        <div
          class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[color:var(--color-accent-ai-soft)] ring-1 ring-[color:var(--color-accent-ai)]/30"
        >
          <i class="pi pi-sparkles text-xs text-[color:var(--color-accent-ai)]"></i>
        </div>
        <div class="bg-glass-1 border-glass shadow-glass rounded-2xl rounded-tl-sm px-5 py-3.5">
          <div class="flex items-center gap-1.5">
            <span class="typing-dot h-2 w-2 rounded-full bg-[color:var(--color-accent-ai)]"></span>
            <span
              class="typing-dot h-2 w-2 rounded-full bg-[color:var(--color-accent-ai)]"
              style="animation-delay: 0.15s"
            ></span>
            <span
              class="typing-dot h-2 w-2 rounded-full bg-[color:var(--color-accent-ai)]"
              style="animation-delay: 0.3s"
            ></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes msg-in {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes typing {
  0%,
  60%,
  100% {
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

@media (prefers-reduced-motion: reduce) {
  .animate-\[msg-in_380ms_var\(--ease-ios\)_both\] {
    animation: none !important;
  }
  .typing-dot {
    animation: none;
    opacity: 0.6;
  }
}
</style>
