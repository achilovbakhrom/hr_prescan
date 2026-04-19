<script setup lang="ts">
/**
 * ChatInterviewPage — candidate chat interview (standalone route).
 *
 * T13 redesign (the "crown jewel"): full-screen chat. AnimatedBackground
 * is mounted directly (no PublicLayout). Vellum is forced on mount to
 * keep the chrome calm while the conversation takes focus. AI avatar ring
 * pulses via `accentPulse` while `isTyping`. No FloatingBackgroundPicker
 * to avoid distracting the candidate.
 */
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import AnimatedBackground from '@/shared/components/AnimatedBackground.vue'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import { useThemeStore } from '@/shared/stores/theme.store'
import { useChatInterview } from '../composables/useChatInterview'
import ChatErrorState from '../components/ChatErrorState.vue'
import ChatMessageList from '../components/ChatMessageList.vue'
import ChatInputBar from '../components/ChatInputBar.vue'
import ChatInterviewHeader from '../components/ChatInterviewHeader.vue'
import ChatMinimizedBar from '../components/ChatMinimizedBar.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()
const token = route.params.token as string

const {
  interview,
  messages,
  inputMessage,
  sending,
  sendingVoice,
  loading,
  isTyping,
  isCompleted,
  errorState,
  errorMessage,
  messagesContainer,
  showLeaveConfirm,
  isMinimized,
  isClosed,
  canSend,
  sendMessage,
  handleVoiceRecorded,
  handleKeyDown,
  handleClose,
  formatTime,
  getAudioUrl,
} = useChatInterview(token)

onMounted(() => {
  if (themeStore.backgroundMode !== 'vellum') {
    themeStore.setBackgroundMode('vellum')
  }
})
</script>

<template>
  <div class="relative flex h-screen flex-col">
    <AnimatedBackground />

    <div v-if="loading" class="relative z-0 flex flex-1 items-center justify-center">
      <div class="text-center">
        <div
          class="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-[color:var(--color-accent-ai-soft)] border-t-[color:var(--color-accent-ai)]"
        ></div>
        <p class="text-sm text-[color:var(--color-text-secondary)]">
          {{ t('interviews.chatPage.preparing') }}
        </p>
      </div>
    </div>

    <ChatErrorState
      v-else-if="errorState"
      class="relative z-0"
      :error-state="errorState"
      :error-message="errorMessage"
    />

    <template v-else-if="interview">
      <ChatMinimizedBar
        v-if="isMinimized && !isClosed"
        :vacancy-title="interview.vacancyTitle"
        :company-name="interview.companyName"
        :message-count="messages.length"
        @restore="isMinimized = false"
        @close="isClosed = true"
      />

      <template v-if="!isMinimized">
        <ChatInterviewHeader
          class="relative z-10"
          :vacancy-title="interview.vacancyTitle"
          :company-name="interview.companyName"
          :is-completed="isCompleted"
          :is-speaking="isTyping"
          @minimize="isMinimized = true"
          @close="handleClose"
        />

        <!-- Leave confirmation dialog -->
        <div
          v-if="showLeaveConfirm"
          class="fixed inset-0 z-50 flex items-center justify-center bg-[color:var(--color-surface-base)]/60 backdrop-blur-sm"
        >
          <GlassSurface level="float" class="mx-4 w-full max-w-sm p-6">
            <div
              class="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-[color:var(--color-warning)]/15"
            >
              <i class="pi pi-exclamation-triangle text-xl text-[color:var(--color-warning)]"></i>
            </div>
            <h2 class="mb-2 text-lg font-semibold text-[color:var(--color-text-primary)]">
              {{ t('interviews.chatPage.leaveTitle') }}
            </h2>
            <p class="mb-5 text-sm text-[color:var(--color-text-secondary)]">
              {{ t('interviews.chatPage.leaveMessage') }}
            </p>
            <div class="flex gap-3">
              <Button
                :label="t('interviews.chatPage.stayButton')"
                class="flex-1"
                @click="showLeaveConfirm = false"
              />
              <Button
                :label="t('interviews.chatPage.leaveButton')"
                severity="secondary"
                outlined
                class="flex-1"
                @click="router.push('/jobs')"
              />
            </div>
          </GlassSurface>
        </div>

        <div ref="messagesContainer" class="relative z-0 flex-1 overflow-y-auto px-4 py-6">
          <ChatMessageList
            :messages="messages"
            :is-typing="isTyping"
            :format-time="formatTime"
            :get-audio-url="getAudioUrl"
          />
        </div>

        <div class="relative z-10">
          <ChatInputBar
            v-model="inputMessage"
            :sending="sending"
            :sending-voice="sendingVoice"
            :can-send="canSend"
            :is-completed="isCompleted"
            @send="sendMessage"
            @keydown="handleKeyDown"
            @voice-recorded="handleVoiceRecorded"
          />
        </div>
      </template>
    </template>
  </div>
</template>
