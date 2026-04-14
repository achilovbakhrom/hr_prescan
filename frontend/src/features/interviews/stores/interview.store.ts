import { ref } from 'vue'
import { defineStore } from 'pinia'
import { extractErrorMessage } from '@/shared/api/errors'
import { interviewService } from '../services/interview.service'
import type {
  ChatMessage,
  Interview,
  InterviewDetail,
} from '../types/interview.types'

export const useInterviewStore = defineStore('interview', () => {
  const interviews = ref<Interview[]>([])
  const currentInterview = ref<InterviewDetail | null>(null)
  const chatMessages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchInterviews(params?: {
    status?: string
  }): Promise<void> {
    loading.value = true
    error.value = null
    try {
      interviews.value = await interviewService.getInterviews(params)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function fetchInterviewDetail(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentInterview.value = await interviewService.getInterviewDetail(id)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function cancelInterview(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const updated = await interviewService.cancelInterview(id)
      if (currentInterview.value?.id === id) {
        currentInterview.value.status = updated.status
      }
      const index = interviews.value.findIndex((i) => i.id === id)
      if (index !== -1) {
        interviews.value[index] = updated
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function getObserverToken(id: string): Promise<string> {
    loading.value = true
    error.value = null
    try {
      const result = await interviewService.getObserverToken(id)
      return result.token
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function fetchCandidateInterview(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentInterview.value =
        await interviewService.getCandidateInterview(id)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function fetchRoomJoinInfo(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentInterview.value = await interviewService.getRoomJoinInfo(id)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function fetchInterviewByToken(token: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentInterview.value = await interviewService.getInterviewByToken(token)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function startInterview(token: string): Promise<InterviewDetail> {
    loading.value = true
    error.value = null
    try {
      const interview = await interviewService.startInterview(token)
      currentInterview.value = interview
      return interview
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function sendChatMessage(token: string, message: string): Promise<ChatMessage> {
    error.value = null
    try {
      const chatMessage = await interviewService.sendChatMessage(token, message)
      chatMessages.value.push(chatMessage)
      return chatMessage
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    }
  }

  async function fetchChatHistory(token: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      chatMessages.value = await interviewService.getChatHistory(token)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function resetInterview(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const updated = await interviewService.resetInterview(id)
      if (currentInterview.value?.id === id) {
        currentInterview.value.status = updated.status
      }
      const index = interviews.value.findIndex((i) => i.id === id)
      if (index !== -1) {
        interviews.value[index] = updated
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  return {
    interviews,
    currentInterview,
    chatMessages,
    loading,
    error,
    fetchInterviews,
    fetchInterviewDetail,
    cancelInterview,
    getObserverToken,
    fetchCandidateInterview,
    fetchRoomJoinInfo,
    fetchInterviewByToken,
    startInterview,
    sendChatMessage,
    fetchChatHistory,
    resetInterview,
  }
})
