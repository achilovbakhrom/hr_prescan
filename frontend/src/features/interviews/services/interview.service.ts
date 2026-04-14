import { apiClient } from '@/shared/api/client'
import type {
  ChatMessage,
  Interview,
  InterviewDetail,
} from '../types/interview.types'

export const interviewService = {
  // HR
  async getInterviews(params?: { status?: string }): Promise<Interview[]> {
    const response = await apiClient.get<Interview[]>('/hr/interviews', {
      params,
    })
    return response.data
  },

  async getInterviewDetail(id: string): Promise<InterviewDetail> {
    const response = await apiClient.get<InterviewDetail>(
      `/hr/interviews/${id}`,
    )
    return response.data
  },

  async cancelInterview(id: string): Promise<Interview> {
    const response = await apiClient.post<Interview>(
      `/hr/interviews/${id}/cancel`,
    )
    return response.data
  },

  async getObserverToken(id: string): Promise<{ token: string }> {
    const response = await apiClient.get<{ token: string }>(
      `/hr/interviews/${id}/observer-token`,
    )
    return response.data
  },

  async resetInterview(interviewId: string): Promise<Interview> {
    const response = await apiClient.post<Interview>(
      `/hr/interviews/${interviewId}/reset/`,
    )
    return response.data
  },

  // Candidate
  async getCandidateInterview(id: string): Promise<InterviewDetail> {
    const response = await apiClient.get<InterviewDetail>(
      `/candidate/interview/${id}`,
    )
    return response.data
  },

  // Public — token-based interview access
  async getInterviewByToken(token: string): Promise<InterviewDetail> {
    const response = await apiClient.get<InterviewDetail>(
      `/public/interview/${token}/`,
    )
    return response.data
  },

  async startInterview(token: string): Promise<InterviewDetail> {
    const response = await apiClient.post<InterviewDetail>(
      `/public/interview/${token}/start/`,
    )
    return response.data
  },

  async sendChatMessage(token: string, message: string): Promise<ChatMessage> {
    const response = await apiClient.post<ChatMessage>(
      `/public/interview/${token}/chat/`,
      { message },
    )
    return response.data
  },

  async getChatHistory(token: string): Promise<ChatMessage[]> {
    const response = await apiClient.get<ChatMessage[]>(
      `/public/interview/${token}/chat/history/`,
    )
    return response.data
  },

  async getRoomJoinInfo(id: string): Promise<InterviewDetail> {
    const response = await apiClient.get<InterviewDetail>(
      `/public/interview/${id}/join`,
    )
    return response.data
  },

  async sendVoiceMessage(
    token: string,
    audioBlob: Blob,
    duration: number,
  ): Promise<{
    aiMessage: ChatMessage
    candidateTranscript: string
    candidateAudioUrl: string
  }> {
    const formData = new FormData()
    formData.append('audio_file', audioBlob, 'voice-message.webm')
    formData.append('duration', String(duration))
    const response = await apiClient.post(
      `/public/interview/${token}/chat/voice`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } },
    )
    return response.data
  },

  getVoiceAudioUrl(token: string, messageIndex: number): string {
    return `${apiClient.defaults.baseURL}/public/interview/${token}/chat/voice/${messageIndex}/audio/`
  },
}
