import { apiClient } from '@/shared/api/client'
import type {
  Interview,
  InterviewDetail,
  ScheduleInterviewRequest,
} from '../types/interview.types'

export const interviewService = {
  // HR
  async scheduleInterview(
    applicationId: string,
    data: ScheduleInterviewRequest,
  ): Promise<Interview> {
    const response = await apiClient.post<Interview>(
      `/applications/${applicationId}/schedule-interview`,
      data,
    )
    return response.data
  },

  async getInterviews(params?: { status?: string }): Promise<Interview[]> {
    const response = await apiClient.get<Interview[]>('/interviews', { params })
    return response.data
  },

  async getInterviewDetail(id: string): Promise<InterviewDetail> {
    const response = await apiClient.get<InterviewDetail>(`/interviews/${id}`)
    return response.data
  },

  async cancelInterview(id: string): Promise<Interview> {
    const response = await apiClient.post<Interview>(
      `/interviews/${id}/cancel`,
    )
    return response.data
  },

  async getObserverToken(id: string): Promise<{ token: string }> {
    const response = await apiClient.get<{ token: string }>(
      `/interviews/${id}/observer-token`,
    )
    return response.data
  },

  // Candidate
  async scheduleByCandidate(
    applicationId: string,
    data: ScheduleInterviewRequest,
  ): Promise<Interview> {
    const response = await apiClient.post<Interview>(
      `/applications/${applicationId}/candidate-schedule`,
      data,
    )
    return response.data
  },

  async getCandidateInterview(id: string): Promise<InterviewDetail> {
    const response = await apiClient.get<InterviewDetail>(
      `/candidate/interviews/${id}`,
    )
    return response.data
  },
}
