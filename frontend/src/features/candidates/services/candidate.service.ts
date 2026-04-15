import { apiClient } from '@/shared/api/client'
import type {
  Application,
  ApplicationDetail,
  ApplicationStatus,
  SubmitApplicationRequest,
} from '../types/candidate.types'
import type { Message } from '../types/message.types'

interface SendEmailPayload {
  subject: string
  body: string
}

interface ScheduleInterviewPayload {
  dateTime: string
  interviewerName: string
  meetingLink?: string
}

export const candidateService = {
  // Public — submit application with CV upload
  async submitApplication(vacancyId: string, data: SubmitApplicationRequest): Promise<Application> {
    const formData = new FormData()
    formData.append('candidate_name', data.candidateName)
    formData.append('candidate_email', data.candidateEmail)
    if (data.candidatePhone) {
      formData.append('candidate_phone', data.candidatePhone)
    }
    if (data.cvFile) {
      formData.append('cv_file', data.cvFile)
    }
    if (data.cvId) {
      formData.append('cv_id', data.cvId)
    }
    const response = await apiClient.post<Application>(
      `/public/vacancies/${vacancyId}/apply`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } },
    )
    return response.data
  },

  // Candidate (auth required)
  async getMyApplications(): Promise<Application[]> {
    const response = await apiClient.get<Application[]>('/candidate/applications')
    return response.data
  },

  async getMyApplicationDetail(id: string): Promise<ApplicationDetail> {
    const response = await apiClient.get<ApplicationDetail>(`/candidate/applications/${id}`)
    return response.data
  },

  // HR
  async getVacancyCandidates(
    vacancyId: string,
    params?: { status?: string; ordering?: string; search?: string },
  ): Promise<Application[]> {
    const response = await apiClient.get<Application[]>(`/hr/vacancies/${vacancyId}/candidates`, {
      params,
    })
    return response.data
  },

  async getAllCandidates(
    params?: { status?: string; ordering?: string; search?: string; vacancyId?: string },
  ): Promise<Application[]> {
    const response = await apiClient.get<Application[]>(
      '/hr/candidates',
      { params },
    )
    return response.data
  },

  async getCandidateDetail(id: string): Promise<ApplicationDetail> {
    const response = await apiClient.get<ApplicationDetail>(`/hr/candidates/${id}`)
    return response.data
  },

  async updateCandidateStatus(id: string, status: ApplicationStatus): Promise<Application> {
    const response = await apiClient.patch<Application>(`/hr/candidates/${id}/status`, { status })
    return response.data
  },

  async addCandidateNote(id: string, note: string): Promise<ApplicationDetail> {
    const response = await apiClient.post<ApplicationDetail>(`/hr/candidates/${id}/notes`, { note })
    return response.data
  },

  // Messaging
  async getMessages(candidateId: string): Promise<Message[]> {
    const response = await apiClient.get<Message[]>(`/hr/candidates/${candidateId}/messages`)
    return response.data
  },

  async sendMessage(candidateId: string, content: string): Promise<Message> {
    const response = await apiClient.post<Message>(`/hr/candidates/${candidateId}/messages`, {
      content,
    })
    return response.data
  },

  // Email
  async sendEmail(candidateId: string, payload: SendEmailPayload): Promise<void> {
    await apiClient.post(`/hr/candidates/${candidateId}/email`, payload)
  },

  // Schedule human interview
  async scheduleHumanInterview(
    candidateId: string,
    payload: ScheduleInterviewPayload,
  ): Promise<void> {
    await apiClient.post(`/hr/candidates/${candidateId}/schedule-human-interview`, payload)
  },

  // Interview data for candidate
  async getCandidateInterview(
    candidateId: string,
    sessionType?: string,
  ): Promise<Record<string, unknown>> {
    const params = sessionType ? { session_type: sessionType } : undefined
    const response = await apiClient.get(`/hr/candidates/${candidateId}/interview`, { params })
    return response.data as Record<string, unknown>
  },

  // CV download
  async getCvDownloadUrl(candidateId: string): Promise<{ url: string; filename: string }> {
    const response = await apiClient.get<{ url: string; filename: string }>(
      `/hr/candidates/${candidateId}/cv-download`,
    )
    return response.data
  },

  // Bulk actions
  async bulkUpdateStatus(applicationIds: string[], status: ApplicationStatus): Promise<void> {
    await apiClient.patch('/hr/candidates/bulk-status', {
      application_ids: applicationIds,
      status,
    })
  },

  // Filtered batch move
  async batchMove(
    vacancyId: string,
    params: {
      fromStatus: ApplicationStatus
      toStatus: ApplicationStatus
      maxScore?: number
      minScore?: number
      scoreField?: 'match_score' | 'prescanning_score' | 'interview_score'
      hasCv?: boolean
      daysSinceApplied?: number
    },
  ): Promise<{ moved: number }> {
    const response = await apiClient.post<{ moved: number }>(
      `/hr/vacancies/${vacancyId}/candidates/batch-move`,
      {
        from_status: params.fromStatus,
        to_status: params.toStatus,
        max_score: params.maxScore,
        min_score: params.minScore,
        score_field: params.scoreField,
        has_cv: params.hasCv,
        days_since_applied: params.daysSinceApplied,
      },
    )
    return response.data
  },

  // Soft delete archived candidates
  async softDelete(applicationIds: string[]): Promise<{ deleted: number }> {
    const response = await apiClient.post<{ deleted: number }>('/hr/candidates/soft-delete', {
      application_ids: applicationIds,
    })
    return response.data
  },
}
