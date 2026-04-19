<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { useChatInterview } from '../composables/useChatInterview'
import ChatErrorState from '../components/ChatErrorState.vue'
import ChatMessageList from '../components/ChatMessageList.vue'
import ChatInputBar from '../components/ChatInputBar.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
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
</script>

<template>
  <div class="flex h-screen flex-col bg-gray-100">
    <!-- Loading -->
    <div v-if="loading" class="flex flex-1 items-center justify-center">
      <div class="text-center">
        <div
          class="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600"
        ></div>
        <p class="text-sm text-gray-500">{{ t('interviews.chatPage.preparing') }}</p>
      </div>
    </div>

    <!-- Error states -->
    <ChatErrorState
      v-else-if="errorState"
      :error-state="errorState"
      :error-message="errorMessage"
    />

    <!-- Chat interface -->
    <template v-else-if="interview">
      <!-- Minimized bar -->
      <div
        v-if="isMinimized && !isClosed"
        class="fixed bottom-0 left-0 right-0 z-50 cursor-pointer border-t border-gray-200 bg-white px-4 py-3 shadow-lg transition-all hover:bg-gray-50"
        @click="isMinimized = false"
      >
        <div class="mx-auto flex max-w-3xl items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600">
              <i class="pi pi-comments text-sm text-white"></i>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900">{{ interview.vacancyTitle }}</p>
              <p v-if="interview.companyName" class="text-xs text-gray-500">
                <i class="pi pi-building mr-0.5"></i>{{ interview.companyName }}
              </p>
              <p class="text-xs text-gray-500">{{ t('interviews.chatPage.inProgress') }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span
              v-if="messages.length"
              class="flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-[10px] font-bold text-white"
            >
              {{ messages.length }}
            </span>
            <i class="pi pi-chevron-up text-gray-400"></i>
            <Button
              icon="pi pi-times"
              severity="secondary"
              text
              rounded
              size="small"
              title="Close"
              @click.stop="isClosed = true"
            />
          </div>
        </div>
      </div>

      <!-- Full chat view -->
      <template v-if="!isMinimized">
        <!-- Header -->
        <header class="border-b border-gray-200 bg-white px-4 py-3 shadow-sm">
          <div class="mx-auto flex max-w-3xl items-center justify-between">
            <div class="flex items-center gap-3">
              <div
                class="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-blue-700"
              >
                <i class="pi pi-comments text-white"></i>
              </div>
              <div>
                <h1 class="text-base font-semibold text-gray-900">{{ interview.vacancyTitle }}</h1>
                <p v-if="interview.companyName" class="text-xs text-gray-500">
                  <i class="pi pi-building mr-1"></i>{{ interview.companyName }}
                </p>
                <div class="flex items-center gap-1.5">
                  <span
                    class="h-2 w-2 rounded-full"
                    :class="isCompleted ? 'bg-gray-400' : 'bg-green-500 animate-pulse'"
                  ></span>
                  <span class="text-xs text-gray-500">{{
                    isCompleted
                      ? t('interviews.status.completed')
                      : t('interviews.chat.aiInterview')
                  }}</span>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-1">
              <button
                class="flex h-9 w-9 items-center justify-center rounded-lg text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
                title="Minimize"
                @click="isMinimized = true"
              >
                <i class="pi pi-minus text-sm"></i>
              </button>
              <button
                class="flex h-9 w-9 items-center justify-center rounded-lg text-gray-400 transition-colors hover:bg-red-50 hover:text-red-500"
                title="Close"
                @click="handleClose"
              >
                <i class="pi pi-times text-sm"></i>
              </button>
            </div>
          </div>
        </header>

        <!-- Leave confirmation dialog -->
        <div
          v-if="showLeaveConfirm"
          class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
        >
          <div class="mx-4 w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl">
            <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-yellow-100">
              <i class="pi pi-exclamation-triangle text-xl text-yellow-600"></i>
            </div>
            <h2 class="mb-2 text-lg font-semibold text-gray-900">
              {{ t('interviews.chatPage.leaveTitle') }}
            </h2>
            <p class="mb-5 text-sm text-gray-500">{{ t('interviews.chatPage.leaveMessage') }}</p>
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
          </div>
        </div>

        <!-- Messages -->
        <div ref="messagesContainer" class="flex-1 overflow-y-auto px-4 py-6">
          <ChatMessageList
            :messages="messages"
            :is-typing="isTyping"
            :format-time="formatTime"
            :get-audio-url="getAudioUrl"
          />
        </div>

        <!-- Input / Completed -->
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
      </template>
    </template>
  </div>
</template>
