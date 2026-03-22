import { apiClient } from '@/shared/api/client'
import type {
  Vacancy,
  VacancyDetail,
  VacancyStatus,
  VacancyCriteria,
  InterviewQuestion,
  CreateVacancyRequest,
  UpdateVacancyRequest,
} from '../types/vacancy.types'

export const vacancyService = {
  // HR endpoints
  async list(params?: { status?: string }): Promise<Vacancy[]> {
    const response = await apiClient.get<Vacancy[]>('/hr/vacancies', { params })
    return response.data
  },

  async create(data: CreateVacancyRequest): Promise<Vacancy> {
    const response = await apiClient.post<Vacancy>('/hr/vacancies', data)
    return response.data
  },

  async getDetail(id: string): Promise<VacancyDetail> {
    const response = await apiClient.get<VacancyDetail>(`/hr/vacancies/${id}`)
    return response.data
  },

  async update(id: string, data: UpdateVacancyRequest): Promise<Vacancy> {
    const response = await apiClient.put<Vacancy>(
      `/hr/vacancies/${id}`,
      data,
    )
    return response.data
  },

  async deleteVacancy(id: string): Promise<void> {
    await apiClient.delete(`/hr/vacancies/${id}`)
  },

  async updateStatus(id: string, status: VacancyStatus): Promise<Vacancy> {
    const statusToAction: Record<string, string> = {
      published: 'publish',
      paused: 'pause',
      archived: 'archive',
    }
    const action = statusToAction[status]
    if (!action) throw new Error(`Invalid status transition: ${status}`)
    const response = await apiClient.patch<Vacancy>(
      `/hr/vacancies/${id}/status`,
      { action },
    )
    return response.data
  },

  // Criteria
  async getCriteria(vacancyId: string): Promise<VacancyCriteria[]> {
    const response = await apiClient.get<VacancyCriteria[]>(
      `/hr/vacancies/${vacancyId}/criteria`,
    )
    return response.data
  },

  async addCriteria(
    vacancyId: string,
    data: { name: string; description?: string; weight?: number; step?: string },
  ): Promise<VacancyCriteria> {
    const response = await apiClient.post<VacancyCriteria>(
      `/hr/vacancies/${vacancyId}/criteria`,
      data,
    )
    return response.data
  },

  async updateCriteria(
    vacancyId: string,
    criteriaId: string,
    data: Partial<VacancyCriteria>,
  ): Promise<VacancyCriteria> {
    const response = await apiClient.put<VacancyCriteria>(
      `/hr/vacancies/${vacancyId}/criteria/${criteriaId}`,
      data,
    )
    return response.data
  },

  async deleteCriteria(vacancyId: string, criteriaId: string): Promise<void> {
    await apiClient.delete(`/hr/vacancies/${vacancyId}/criteria/${criteriaId}`)
  },

  // Questions
  async getQuestions(vacancyId: string): Promise<InterviewQuestion[]> {
    const response = await apiClient.get<InterviewQuestion[]>(
      `/hr/vacancies/${vacancyId}/questions`,
    )
    return response.data
  },

  async addQuestion(
    vacancyId: string,
    data: { text: string; category?: string; step?: string },
  ): Promise<InterviewQuestion> {
    const response = await apiClient.post<InterviewQuestion>(
      `/hr/vacancies/${vacancyId}/questions`,
      data,
    )
    return response.data
  },

  async updateQuestion(
    vacancyId: string,
    questionId: string,
    data: Partial<InterviewQuestion>,
  ): Promise<InterviewQuestion> {
    const response = await apiClient.put<InterviewQuestion>(
      `/hr/vacancies/${vacancyId}/questions/${questionId}`,
      data,
    )
    return response.data
  },

  async deleteQuestion(
    vacancyId: string,
    questionId: string,
  ): Promise<void> {
    await apiClient.delete(
      `/hr/vacancies/${vacancyId}/questions/${questionId}`,
    )
  },

  async parseCompanyFile(file: File): Promise<string> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post<{ companyInfo: string }>(
      '/hr/vacancies/parse-company-file',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } },
    )
    return response.data.companyInfo
  },

  async parseCompanyUrl(url: string): Promise<string> {
    const response = await apiClient.post<{ companyInfo: string }>(
      '/hr/vacancies/parse-company-url',
      { url },
    )
    return response.data.companyInfo
  },

  async generateQuestions(vacancyId: string): Promise<InterviewQuestion[]> {
    const response = await apiClient.post<InterviewQuestion[]>(
      `/hr/vacancies/${vacancyId}/questions/generate`,
    )
    return response.data
  },

  async regenerateKeywords(id: string): Promise<{ keywords: string[] }> {
    const response = await apiClient.post<{ keywords: string[] }>(`/hr/vacancies/${id}/regenerate-keywords`)
    return response.data
  },

  // Public
  async getPublicList(params?: {
    search?: string
    location?: string
    isRemote?: boolean
    employmentType?: string
    experienceLevel?: string
    salaryMin?: number
    salaryMax?: number
  }): Promise<Vacancy[]> {
    const response = await apiClient.get<Vacancy[]>('/public/vacancies', {
      params,
    })
    return response.data
  },

  async getPublicDetail(id: string): Promise<Vacancy> {
    const response = await apiClient.get<Vacancy>(`/public/vacancies/${id}`)
    return response.data
  },

  async getByShareToken(token: string): Promise<Vacancy> {
    const response = await apiClient.get<Vacancy>(
      `/public/vacancies/share/${token}`,
    )
    return response.data
  },
}
