import { apiClient } from '@/shared/api/client'
import type {
  Application,
  ApplicationDetail,
  ApplicationStatus,
  SubmitApplicationRequest,
} from '../types/candidate.types'

export const candidateService = {
  // Public — submit application with CV upload
  async submitApplication(
    vacancyId: string,
    data: SubmitApplicationRequest,
  ): Promise<Application> {
    const formData = new FormData()
    formData.append('candidate_name', data.candidateName)
    formData.append('candidate_email', data.candidateEmail)
    if (data.candidatePhone) {
      formData.append('candidate_phone', data.candidatePhone)
    }
    if (data.cvFile) {
      formData.append('cv_file', data.cvFile)
    }
    const response = await apiClient.post<Application>(
      `/jobs/${vacancyId}/apply`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } },
    )
    return response.data
  },

  // Candidate (auth required)
  async getMyApplications(): Promise<Application[]> {
    const response = await apiClient.get<Application[]>('/my-applications')
    return response.data
  },

  async getMyApplicationDetail(id: string): Promise<ApplicationDetail> {
    const response = await apiClient.get<ApplicationDetail>(
      `/my-applications/${id}`,
    )
    return response.data
  },

  // HR
  async getVacancyCandidates(
    vacancyId: string,
    params?: { status?: string; ordering?: string },
  ): Promise<Application[]> {
    const response = await apiClient.get<Application[]>(
      `/vacancies/${vacancyId}/candidates`,
      { params },
    )
    return response.data
  },

  async getCandidateDetail(id: string): Promise<ApplicationDetail> {
    const response = await apiClient.get<ApplicationDetail>(
      `/candidates/${id}`,
    )
    return response.data
  },

  async updateCandidateStatus(
    id: string,
    status: ApplicationStatus,
  ): Promise<Application> {
    const response = await apiClient.patch<Application>(
      `/candidates/${id}/status`,
      { status },
    )
    return response.data
  },

  async addCandidateNote(
    id: string,
    note: string,
  ): Promise<ApplicationDetail> {
    const response = await apiClient.patch<ApplicationDetail>(
      `/candidates/${id}/notes`,
      { hr_notes: note },
    )
    return response.data
  },
}
