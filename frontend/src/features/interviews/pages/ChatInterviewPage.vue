<script setup lang="ts">
import { ref, computed, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import { interviewService } from '../services/interview.service'
import type { ChatMessage, InterviewDetail } from '../types/interview.types'
import VoiceRecordButton from '../components/VoiceRecordButton.vue'
import VoiceMessageBubble from '../components/VoiceMessageBubble.vue'

const route = useRoute()
const router = useRouter()
const token = route.params.token as string
const showLeaveConfirm = ref(false)
const isMinimized = ref(false)
const isClosed = ref(false)

const interview = ref<InterviewDetail | null>(null)
const messages = ref<ChatMessage[]>([])
const inputMessage = ref('')
const sending = ref(false)
const sendingVoice = ref(false)
const loading = ref(true)
const isTyping = ref(false)
const isCompleted = ref(false)
const errorState = ref<'expired' | 'closed' | 'completed' | 'error' | null>(null)
const errorMessage = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

const canSend = computed(() => inputMessage.value.trim().length > 0 && !sending.value && !isCompleted.value)

// Prevent accidental page close
function beforeUnloadHandler(e: BeforeUnloadEvent) {
  if (!isCompleted.value && messages.value.length > 0) {
    e.preventDefault()
  }
}

onMounted(async () => {
  window.addEventListener('beforeunload', beforeUnloadHandler)

  try {
    const data = await interviewService.getInterviewByToken(token)
    interview.value = data

    if (data.status === 'completed') {
      errorState.value = 'completed'
      loading.value = false
      return
    }
    if (data.status === 'expired') {
      errorState.value = 'expired'
      loading.value = false
      return
    }
    if (data.status === 'cancelled') {
      errorState.value = 'closed'
      loading.value = false
      return
    }

    if (data.status === 'pending') {
      const started = await interviewService.startInterview(token)
      interview.value = started
      if (started.chatHistory && started.chatHistory.length > 0) {
        messages.value = started.chatHistory
      }
    } else if (data.status === 'in_progress') {
      const history = await interviewService.getChatHistory(token)
      messages.value = history
    }

    loading.value = false
    await nextTick()
    scrollToBottom()
  } catch (err: unknown) {
    const axiosErr = err as { response?: { status?: number; data?: { detail?: string; message?: string } } }
    const status = axiosErr.response?.status
    const detail = axiosErr.response?.data?.detail ?? axiosErr.response?.data?.message ?? ''

    if (status === 410 || detail.toLowerCase().includes('expired')) {
      errorState.value = 'expired'
      errorMessage.value = detail || 'This interview link has expired.'
    } else if (detail.toLowerCase().includes('closed')) {
      errorState.value = 'closed'
      errorMessage.value = detail || 'This vacancy is no longer accepting applications.'
    } else {
      errorState.value = 'error'
      errorMessage.value = detail || 'Failed to load the interview. Please try again.'
    }
    loading.value = false
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', beforeUnloadHandler)
})

function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

async function sendMessage(): Promise<void> {
  const text = inputMessage.value.trim()
  if (!text || sending.value || isCompleted.value) return

  messages.value.push({
    role: 'candidate',
    text,
    timestamp: new Date().toISOString(),
  })
  inputMessage.value = ''
  sending.value = true

  await nextTick()
  scrollToBottom()

  // Show typing indicator after a brief pause (feels more natural)
  await delay(500)
  isTyping.value = true
  await nextTick()
  scrollToBottom()

  try {
    const aiReply = await interviewService.sendChatMessage(token, text)

    // Add artificial delay for humanlike feel (1-2 seconds)
    const typingDelay = 1000 + Math.random() * 1000
    await delay(typingDelay)

    isTyping.value = false
    messages.value.push(aiReply)

    if (aiReply.text.includes('[INTERVIEW_COMPLETE]') || aiReply.text.includes('[END]')) {
      isCompleted.value = true
      const lastMsg = messages.value[messages.value.length - 1]
      lastMsg.text = lastMsg.text.replace(/\[INTERVIEW_COMPLETE\]/g, '').replace(/\[END\]/g, '').trim()
    }

    try {
      const updated = await interviewService.getInterviewByToken(token)
      if (updated.status === 'completed') {
        isCompleted.value = true
      }
    } catch {
      // non-critical
    }

    await nextTick()
    scrollToBottom()
  } catch {
    isTyping.value = false
    messages.value.push({
      role: 'ai',
      text: 'Sorry, there was an error. Please try sending your message again.',
      timestamp: new Date().toISOString(),
    })
    await nextTick()
    scrollToBottom()
  } finally {
    sending.value = false
  }
}

function handleKeyDown(event: KeyboardEvent): void {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

function scrollToBottom(): void {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function formatTime(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function getAudioUrl(index: number): string {
  return interviewService.getVoiceAudioUrl(token, index)
}

async function handleVoiceRecorded(blob: Blob, voiceDuration: number): Promise<void> {
  if (sendingVoice.value || isCompleted.value) return

  sendingVoice.value = true

  messages.value.push({
    role: 'candidate',
    text: 'Transcribing...',
    timestamp: new Date().toISOString(),
    messageType: 'voice',
    duration: voiceDuration,
  })

  await nextTick()
  scrollToBottom()

  isTyping.value = true
  await nextTick()
  scrollToBottom()

  try {
    const result = await interviewService.sendVoiceMessage(token, blob, voiceDuration)

    // Update placeholder with real transcript (audioUrl uses getAudioUrl(idx) in template)
    const lastCandidateIdx = messages.value.length - 1
    const lastCandidateMsg = messages.value[lastCandidateIdx]
    if (lastCandidateMsg && lastCandidateMsg.role === 'candidate') {
      lastCandidateMsg.text = result.candidateTranscript
    }

    isTyping.value = false
    messages.value.push(result.aiMessage)

    if (result.aiMessage.text.includes('[INTERVIEW_COMPLETE]') || result.aiMessage.text.includes('[END]')) {
      isCompleted.value = true
      const lastMsg = messages.value[messages.value.length - 1]
      lastMsg.text = lastMsg.text.replace(/\[INTERVIEW_COMPLETE\]/g, '').replace(/\[END\]/g, '').trim()
    }

    try {
      const updated = await interviewService.getInterviewByToken(token)
      if (updated.status === 'completed') {
        isCompleted.value = true
      }
    } catch {
      // non-critical
    }
  } catch {
    isTyping.value = false
    // Remove the placeholder message
    const lastIdx = messages.value.length - 1
    if (messages.value[lastIdx]?.role === 'candidate' && messages.value[lastIdx]?.text === 'Transcribing...') {
      messages.value.pop()
    }
    messages.value.push({
      role: 'ai',
      text: 'Sorry, there was an error processing your voice message. Please try again.',
      timestamp: new Date().toISOString(),
    })
  } finally {
    sendingVoice.value = false
    await nextTick()
    scrollToBottom()
  }
}

function handleClose(): void {
  if (isCompleted.value) {
    router.push('/jobs')
  } else {
    showLeaveConfirm.value = true
  }
}
</script>

<template>
  <div class="flex h-screen flex-col bg-gray-100">
    <!-- Loading -->
    <div v-if="loading" class="flex flex-1 items-center justify-center">
      <div class="text-center">
        <div class="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600"></div>
        <p class="text-sm text-gray-500">Preparing your interview...</p>
      </div>
    </div>

    <!-- Error states -->
    <div v-else-if="errorState" class="flex flex-1 items-center justify-center px-4">
      <div class="w-full max-w-md text-center">
        <template v-if="errorState === 'completed'">
          <div class="rounded-2xl bg-white p-8 shadow-lg">
            <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
              <i class="pi pi-check text-3xl text-green-600"></i>
            </div>
            <h1 class="mb-2 text-xl font-bold text-gray-900">Interview Completed</h1>
            <p class="mb-6 text-sm text-gray-500">
              Your responses are being reviewed. We'll be in touch soon.
            </p>
            <RouterLink
              to="/jobs"
              class="inline-block rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
            >
              Browse more jobs
            </RouterLink>
          </div>
        </template>
        <template v-else-if="errorState === 'expired'">
          <div class="rounded-2xl bg-white p-8 shadow-lg">
            <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-yellow-100">
              <i class="pi pi-clock text-3xl text-yellow-600"></i>
            </div>
            <h1 class="mb-2 text-xl font-bold text-gray-900">Link Expired</h1>
            <p class="mb-6 text-sm text-gray-500">{{ errorMessage || 'This interview link has expired.' }}</p>
            <RouterLink to="/jobs" class="text-sm font-medium text-blue-600 hover:underline">Browse more jobs</RouterLink>
          </div>
        </template>
        <template v-else-if="errorState === 'closed'">
          <div class="rounded-2xl bg-white p-8 shadow-lg">
            <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gray-100">
              <i class="pi pi-ban text-3xl text-gray-400"></i>
            </div>
            <h1 class="mb-2 text-xl font-bold text-gray-900">Vacancy Closed</h1>
            <p class="mb-6 text-sm text-gray-500">{{ errorMessage || 'This vacancy is no longer accepting applications.' }}</p>
            <RouterLink to="/jobs" class="text-sm font-medium text-blue-600 hover:underline">Browse more jobs</RouterLink>
          </div>
        </template>
        <template v-else>
          <div class="rounded-2xl bg-white p-8 shadow-lg">
            <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
              <i class="pi pi-exclamation-triangle text-3xl text-red-400"></i>
            </div>
            <h1 class="mb-2 text-xl font-bold text-gray-900">Something Went Wrong</h1>
            <p class="mb-6 text-sm text-gray-500">{{ errorMessage }}</p>
            <Button label="Try Again" icon="pi pi-refresh" rounded @click="$router.go(0)" />
          </div>
        </template>
      </div>
    </div>

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
              <p class="text-xs text-gray-500">AI Interview in progress - click to expand</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span v-if="messages.length" class="flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-[10px] font-bold text-white">
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
              <div class="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-blue-700">
                <i class="pi pi-comments text-white"></i>
              </div>
              <div>
                <h1 class="text-base font-semibold text-gray-900">{{ interview.vacancyTitle }}</h1>
                <div class="flex items-center gap-1.5">
                  <span class="h-2 w-2 rounded-full" :class="isCompleted ? 'bg-gray-400' : 'bg-green-500 animate-pulse'"></span>
                  <span class="text-xs text-gray-500">{{ isCompleted ? 'Interview completed' : 'AI Interviewer' }}</span>
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
        <div v-if="showLeaveConfirm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div class="mx-4 w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl">
            <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-yellow-100">
              <i class="pi pi-exclamation-triangle text-xl text-yellow-600"></i>
            </div>
            <h2 class="mb-2 text-lg font-semibold text-gray-900">Leave interview?</h2>
            <p class="mb-5 text-sm text-gray-500">
              Your progress is saved. You can return anytime using the same link.
            </p>
            <div class="flex gap-3">
              <Button
                label="Continue Interview"
                class="flex-1"
                @click="showLeaveConfirm = false"
              />
              <Button
                label="Leave"
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
          <div class="mx-auto max-w-3xl space-y-4">
            <!-- Date header -->
            <div class="flex items-center justify-center">
              <span class="rounded-full bg-gray-200 px-3 py-1 text-[10px] font-medium text-gray-500">
                Today
              </span>
            </div>

            <div v-for="(msg, idx) in messages" :key="idx" class="flex" :class="msg.role === 'candidate' ? 'justify-end' : 'justify-start'">
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
                  <!-- Still transcribing — show placeholder -->
                  <div v-if="msg.text === 'Transcribing...'" class="flex items-center gap-2 text-white/80">
                    <i class="pi pi-spinner pi-spin text-xs"></i>
                    <span class="text-[13px]">Transcribing voice message...</span>
                  </div>
                  <!-- Transcribed — show playable voice bubble -->
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
        </div>

        <!-- Completed overlay -->
        <div v-if="isCompleted" class="border-t border-gray-200 bg-white px-4 py-6">
          <div class="mx-auto max-w-3xl text-center">
            <div class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-green-100">
              <i class="pi pi-check text-2xl text-green-600"></i>
            </div>
            <h2 class="mb-1 text-lg font-semibold text-gray-900">Interview Complete!</h2>
            <p class="mb-4 text-sm text-gray-500">
              Thank you for your time. We'll review your responses and be in touch.
            </p>
            <div class="flex justify-center gap-3">
              <RouterLink
                to="/register"
                class="rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
              >
                Create Account to Track Status
              </RouterLink>
              <RouterLink
                to="/jobs"
                class="rounded-xl border border-gray-300 px-5 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
              >
                Browse More Jobs
              </RouterLink>
            </div>
          </div>
        </div>

        <!-- Input area -->
        <div v-if="!isCompleted" class="border-t border-gray-200 bg-white px-4 py-3">
          <div class="mx-auto flex max-w-3xl items-end gap-3">
            <div class="relative flex-1">
              <textarea
                v-model="inputMessage"
                rows="1"
                class="w-full resize-none rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 pr-4 text-sm transition-colors placeholder:text-gray-400 focus:border-blue-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100"
                placeholder="Type your answer..."
                :disabled="sending || sendingVoice"
                @keydown="handleKeyDown"
              ></textarea>
            </div>
            <VoiceRecordButton
              v-if="!inputMessage.trim()"
              :disabled="sending || sendingVoice || isCompleted"
              @recorded="handleVoiceRecorded"
            />
            <button
              v-else
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full transition-all"
              :class="canSend ? 'bg-blue-600 text-white shadow-md hover:bg-blue-700 hover:shadow-lg' : 'bg-gray-200 text-gray-400'"
              :disabled="!canSend"
              @click="sendMessage"
            >
              <i v-if="!sending" class="pi pi-send text-sm" style="transform: rotate(-30deg)"></i>
              <i v-else class="pi pi-spinner pi-spin text-sm"></i>
            </button>
          </div>
          <p class="mx-auto mt-1.5 max-w-3xl text-center text-[10px] text-gray-400">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </template>
    </template>
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
