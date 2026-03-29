import { ref, computed, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { interviewService } from '../services/interview.service'
import type { ChatMessage, InterviewDetail } from '../types/interview.types'

export type ChatErrorState = 'expired' | 'closed' | 'completed' | 'error' | null

export function useChatInterview(token: string) {
  const router = useRouter()
  const interview = ref<InterviewDetail | null>(null)
  const messages = ref<ChatMessage[]>([])
  const inputMessage = ref('')
  const sending = ref(false)
  const sendingVoice = ref(false)
  const loading = ref(true)
  const isTyping = ref(false)
  const isCompleted = ref(false)
  const errorState = ref<ChatErrorState>(null)
  const errorMessage = ref('')
  const messagesContainer = ref<HTMLElement | null>(null)
  const showLeaveConfirm = ref(false)
  const isMinimized = ref(false)
  const isClosed = ref(false)
  const canSend = computed(() => inputMessage.value.trim().length > 0 && !sending.value && !isCompleted.value)

  function beforeUnloadHandler(e: BeforeUnloadEvent) { if (!isCompleted.value && messages.value.length > 0) e.preventDefault() }
  function scrollToBottom(): void { if (messagesContainer.value) messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight }
  function delay(ms: number): Promise<void> { return new Promise((r) => setTimeout(r, ms)) }
  function formatTime(ts: string): string { return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
  function getAudioUrl(index: number): string { return interviewService.getVoiceAudioUrl(token, index) }

  function checkInterviewComplete(text: string): void {
    if (text.includes('[INTERVIEW_COMPLETE]') || text.includes('[END]')) {
      isCompleted.value = true
      const last = messages.value[messages.value.length - 1]
      last.text = last.text.replace(/\[INTERVIEW_COMPLETE\]/g, '').replace(/\[END\]/g, '').trim()
    }
  }
  async function refreshStatus(): Promise<void> {
    try { if ((await interviewService.getInterviewByToken(token)).status === 'completed') isCompleted.value = true } catch { /* non-critical */ }
  }

  async function sendMessage(): Promise<void> {
    const text = inputMessage.value.trim()
    if (!text || sending.value || isCompleted.value) return
    messages.value.push({ role: 'candidate', text, timestamp: new Date().toISOString() })
    inputMessage.value = ''
    sending.value = true
    await nextTick(); scrollToBottom()
    await delay(500); isTyping.value = true; await nextTick(); scrollToBottom()
    try {
      const aiReply = await interviewService.sendChatMessage(token, text)
      await delay(1000 + Math.random() * 1000)
      isTyping.value = false
      messages.value.push(aiReply)
      checkInterviewComplete(aiReply.text)
      await refreshStatus()
    } catch {
      isTyping.value = false
      messages.value.push({ role: 'ai', text: 'Sorry, there was an error. Please try sending your message again.', timestamp: new Date().toISOString() })
    } finally { sending.value = false; await nextTick(); scrollToBottom() }
  }

  async function handleVoiceRecorded(blob: Blob, voiceDuration: number): Promise<void> {
    if (sendingVoice.value || isCompleted.value) return
    sendingVoice.value = true
    messages.value.push({ role: 'candidate', text: 'Transcribing...', timestamp: new Date().toISOString(), messageType: 'voice', duration: voiceDuration })
    await nextTick(); scrollToBottom(); isTyping.value = true; await nextTick(); scrollToBottom()
    try {
      const result = await interviewService.sendVoiceMessage(token, blob, voiceDuration)
      const lastMsg = messages.value[messages.value.length - 1]
      if (lastMsg?.role === 'candidate') lastMsg.text = result.candidateTranscript
      isTyping.value = false
      messages.value.push(result.aiMessage)
      checkInterviewComplete(result.aiMessage.text)
      await refreshStatus()
    } catch {
      isTyping.value = false
      const li = messages.value.length - 1
      if (messages.value[li]?.role === 'candidate' && messages.value[li]?.text === 'Transcribing...') messages.value.pop()
      messages.value.push({ role: 'ai', text: 'Sorry, there was an error processing your voice message. Please try again.', timestamp: new Date().toISOString() })
    } finally { sendingVoice.value = false; await nextTick(); scrollToBottom() }
  }

  function handleKeyDown(event: KeyboardEvent): void { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); sendMessage() } }
  function handleClose(): void { isCompleted.value ? router.push('/jobs') : (showLeaveConfirm.value = true) }

  onMounted(async () => {
    window.addEventListener('beforeunload', beforeUnloadHandler)
    try {
      const data = await interviewService.getInterviewByToken(token)
      interview.value = data
      if (data.status === 'completed') { errorState.value = 'completed'; loading.value = false; return }
      if (data.status === 'expired') { errorState.value = 'expired'; loading.value = false; return }
      if (data.status === 'cancelled') { errorState.value = 'closed'; loading.value = false; return }
      if (data.status === 'pending') {
        const started = await interviewService.startInterview(token)
        interview.value = started
        if (started.chatHistory?.length) messages.value = started.chatHistory
      } else if (data.status === 'in_progress') {
        messages.value = await interviewService.getChatHistory(token)
      }
      loading.value = false; await nextTick(); scrollToBottom()
    } catch (err: unknown) {
      const ax = err as { response?: { status?: number; data?: { detail?: string; message?: string } } }
      const status = ax.response?.status
      const detail = ax.response?.data?.detail ?? ax.response?.data?.message ?? ''
      if (status === 410 || detail.toLowerCase().includes('expired')) { errorState.value = 'expired'; errorMessage.value = detail || 'This interview link has expired.' }
      else if (detail.toLowerCase().includes('closed')) { errorState.value = 'closed'; errorMessage.value = detail || 'This vacancy is no longer accepting applications.' }
      else { errorState.value = 'error'; errorMessage.value = detail || 'Failed to load the interview. Please try again.' }
      loading.value = false
    }
  })
  onBeforeUnmount(() => { window.removeEventListener('beforeunload', beforeUnloadHandler) })

  return {
    interview, messages, inputMessage, sending, sendingVoice, loading, isTyping, isCompleted,
    errorState, errorMessage, messagesContainer, showLeaveConfirm, isMinimized, isClosed, canSend,
    sendMessage, handleVoiceRecorded, handleKeyDown, handleClose, formatTime, getAudioUrl, scrollToBottom,
  }
}
