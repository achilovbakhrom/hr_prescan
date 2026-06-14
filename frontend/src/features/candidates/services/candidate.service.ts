import { apiClient } from '@/shared/api/client'
import type {
  Application,
  ApplicationDetail,
  HRCandidateRecord,
  HRCandidateRecordDetail,
  HRCandidateRecordUpdate,
  ApplicationStatus,
  SubmitApplicationRequest,
} from '../types/candidate.types'
import type { Message } from '../types/message.types'
import type { DecisionSupport } from '@/shared/types/interview.types'

interface SendEmailPayload {
  subject: string
  body: string
}

interface ScheduleInterviewPayload {
  dateTime: string
  interviewerName: string
  meetingLink?: string
}

export interface PublicCandidateReviewSession {
  id: string
  sessionType: 'prescanning' | 'interview'
  screeningMode: 'chat' | 'meet'
  status: string
  overallScore: number | null
  aiSummary: string
  aiSummaryTranslations: Record<string, string>
  decisionSupport: DecisionSupport
  transcript: Array<{ speaker?: string; role?: string; text: string; timestamp?: number | string }>
  chatHistory: Array<{ role: 'ai' | 'candidate'; text: string; timestamp?: string | number }>
  recordingPath: string
  scores: Array<{
    id: string
    criteria: string
    criteriaName: string
    criteriaTranslations?: Record<string, string>
    score: number
    aiNotes: string
    aiNotesTranslations: Record<string, string>
    evidence?: Array<{
      quote: string
      timestamp?: number | null
      speaker?: string
      line?: number | null
    }>
  }>
  createdAt: string
  completedAt: string | null
}

export interface PublicCandidateReview {
  candidate: {
    id: string
    candidateName: string
    candidateEmail: string
    vacancyTitle: string
    companyName: string
    status: ApplicationStatus
    matchScore: number | null
    createdAt: string
  }
  sessions: PublicCandidateReviewSession[]
}

export interface HiringManagerFeedback {
  id: string
  reviewerName: string
  reviewerRole: string
  recommendation: 'advance' | 'maybe' | 'reject'
  rating: number | null
  comment: string
  createdAt: string
}

export interface SubmitHiringManagerFeedbackPayload {
  reviewerName: string
  reviewerRole?: string
  recommendation: 'advance' | 'maybe' | 'reject'
  rating?: number | null
  comment?: string
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
    if (data.profilePhoto) {
      formData.append('profile_photo', data.profilePhoto)
    }
    if (data.linkedinUrl) {
      formData.append('linkedin_url', data.linkedinUrl)
    }
    if (data.coverNote) {
      formData.append('cover_note', data.coverNote)
    }
    formData.append('prescreen_consent', data.prescreenConsent ? 'true' : 'false')
    const response = await apiClient.post<Application>(
      `/public/vacancies/${vacancyId}/apply/`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } },
    )
    return response.data
  },

  // Candidate (auth required)
  async getMyApplications(): Promise<Application[]> {
    const response = await apiClient.get<Application[]>('/candidate/applications/')
    return response.data
  },

  async getMyApplicationDetail(id: string): Promise<ApplicationDetail> {
    const response = await apiClient.get<ApplicationDetail>(`/candidate/applications/${id}/`)
    return response.data
  },

  // HR
  async getVacancyCandidates(
    vacancyId: string,
    params?: { status?: string; ordering?: string; search?: string },
  ): Promise<Application[]> {
    const response = await apiClient.get<Application[]>(`/hr/vacancies/${vacancyId}/candidates/`, {
      params,
    })
    return response.data
  },

  async getAllCandidates(params?: {
    status?: string
    ordering?: string
    search?: string
    vacancyId?: string
  }): Promise<Application[]> {
    const response = await apiClient.get<Application[]>('/hr/candidates/', { params })
    return response.data
  },

  async getCandidateDetail(id: string): Promise<ApplicationDetail> {
    const response = await apiClient.get<ApplicationDetail>(`/hr/candidates/${id}/`)
    return response.data
  },

  async getCandidateBase(params?: {
    search?: string
    ordering?: string
  }): Promise<HRCandidateRecord[]> {
    const response = await apiClient.get<HRCandidateRecord[]>('/hr/candidate-base/', { params })
    return response.data
  },

  async getCandidateBaseDetail(id: string): Promise<HRCandidateRecordDetail> {
    const response = await apiClient.get<HRCandidateRecordDetail>(`/hr/candidate-base/${id}/`)
    return response.data
  },

  async updateCandidateBase(
    id: string,
    data: HRCandidateRecordUpdate,
  ): Promise<HRCandidateRecordDetail> {
    const response = await apiClient.patch<HRCandidateRecordDetail>(
      `/hr/candidate-base/${id}/`,
      data,
    )
    return response.data
  },

  async deleteCandidateBase(id: string): Promise<void> {
    await apiClient.delete(`/hr/candidate-base/${id}/`)
  },

  async updateCandidateStatus(id: string, status: ApplicationStatus): Promise<Application> {
    const response = await apiClient.patch<Application>(`/hr/candidates/${id}/status/`, { status })
    return response.data
  },

  async addCandidateNote(id: string, note: string): Promise<ApplicationDetail> {
    const response = await apiClient.post<ApplicationDetail>(`/hr/candidates/${id}/notes/`, {
      note,
    })
    return response.data
  },

  async resetScreening(
    id: string,
    sessionType: 'prescanning' | 'interview',
  ): Promise<ApplicationDetail> {
    const response = await apiClient.post<ApplicationDetail>(
      `/hr/candidates/${id}/screening/${sessionType}/reset/`,
    )
    return response.data
  },

  // Messaging
  async getMessages(candidateId: string): Promise<Message[]> {
    const response = await apiClient.get<Message[]>(`/hr/candidates/${candidateId}/messages/`)
    return response.data
  },

  async sendMessage(candidateId: string, content: string): Promise<Message> {
    const response = await apiClient.post<Message>(`/hr/candidates/${candidateId}/messages/`, {
      content,
    })
    return response.data
  },

  // Email
  async sendEmail(candidateId: string, payload: SendEmailPayload): Promise<void> {
    await apiClient.post(`/hr/candidates/${candidateId}/email/`, payload)
  },

  // Schedule human interview
  async scheduleHumanInterview(
    candidateId: string,
    payload: ScheduleInterviewPayload,
  ): Promise<void> {
    await apiClient.post(`/hr/candidates/${candidateId}/schedule-human-interview/`, payload)
  },

  // Interview data for candidate
  async getCandidateInterview(
    candidateId: string,
    sessionType?: string,
  ): Promise<Record<string, unknown>> {
    const params = sessionType ? { session_type: sessionType } : undefined
    const response = await apiClient.get(`/hr/candidates/${candidateId}/interview/`, { params })
    return response.data as Record<string, unknown>
  },

  // CV download
  async getCvDownloadUrl(candidateId: string): Promise<{ url: string; filename: string }> {
    const response = await apiClient.get<{ url: string; filename: string }>(
      `/hr/candidates/${candidateId}/cv-download/`,
    )
    return response.data
  },

  // Bulk actions
  async bulkUpdateStatus(applicationIds: string[], status: ApplicationStatus): Promise<void> {
    await apiClient.patch('/hr/candidates/bulk-status/', {
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
      `/hr/vacancies/${vacancyId}/candidates/batch-move/`,
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
    const response = await apiClient.post<{ deleted: number }>('/hr/candidates/soft-delete/', {
      application_ids: applicationIds,
    })
    return response.data
  },

  async rotateHiringManagerToken(candidateId: string): Promise<{ hiringManagerToken: string }> {
    const response = await apiClient.post<{ hiringManagerToken: string }>(
      `/hr/candidates/${candidateId}/share-token/rotate/`,
    )
    return response.data
  },

  async getPublicCandidateReview(token: string): Promise<PublicCandidateReview> {
    const response = await apiClient.get<PublicCandidateReview>(
      `/public/candidates/review/${token}/`,
    )
    return response.data
  },

  async submitHiringManagerFeedback(
    token: string,
    payload: SubmitHiringManagerFeedbackPayload,
  ): Promise<HiringManagerFeedback> {
    const response = await apiClient.post<HiringManagerFeedback>(
      `/public/candidates/review/${token}/`,
      payload,
    )
    return response.data
  },
}
