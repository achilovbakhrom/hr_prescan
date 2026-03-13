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
    const response = await apiClient.get<Vacancy[]>('/vacancies', { params })
    return response.data
  },

  async create(data: CreateVacancyRequest): Promise<Vacancy> {
    const response = await apiClient.post<Vacancy>('/vacancies', data)
    return response.data
  },

  async getDetail(id: string): Promise<VacancyDetail> {
    const response = await apiClient.get<VacancyDetail>(`/vacancies/${id}`)
    return response.data
  },

  async update(id: string, data: UpdateVacancyRequest): Promise<Vacancy> {
    const response = await apiClient.patch<Vacancy>(`/vacancies/${id}`, data)
    return response.data
  },

  async updateStatus(id: string, status: VacancyStatus): Promise<Vacancy> {
    const response = await apiClient.patch<Vacancy>(
      `/vacancies/${id}/status`,
      { status },
    )
    return response.data
  },

  // Criteria
  async getCriteria(vacancyId: string): Promise<VacancyCriteria[]> {
    const response = await apiClient.get<VacancyCriteria[]>(
      `/vacancies/${vacancyId}/criteria`,
    )
    return response.data
  },

  async addCriteria(
    vacancyId: string,
    data: { name: string; description?: string; weight?: number },
  ): Promise<VacancyCriteria> {
    const response = await apiClient.post<VacancyCriteria>(
      `/vacancies/${vacancyId}/criteria`,
      data,
    )
    return response.data
  },

  async updateCriteria(
    vacancyId: string,
    criteriaId: string,
    data: Partial<VacancyCriteria>,
  ): Promise<VacancyCriteria> {
    const response = await apiClient.patch<VacancyCriteria>(
      `/vacancies/${vacancyId}/criteria/${criteriaId}`,
      data,
    )
    return response.data
  },

  async deleteCriteria(vacancyId: string, criteriaId: string): Promise<void> {
    await apiClient.delete(`/vacancies/${vacancyId}/criteria/${criteriaId}`)
  },

  // Questions
  async getQuestions(vacancyId: string): Promise<InterviewQuestion[]> {
    const response = await apiClient.get<InterviewQuestion[]>(
      `/vacancies/${vacancyId}/questions`,
    )
    return response.data
  },

  async addQuestion(
    vacancyId: string,
    data: { text: string; category?: string },
  ): Promise<InterviewQuestion> {
    const response = await apiClient.post<InterviewQuestion>(
      `/vacancies/${vacancyId}/questions`,
      data,
    )
    return response.data
  },

  async updateQuestion(
    vacancyId: string,
    questionId: string,
    data: Partial<InterviewQuestion>,
  ): Promise<InterviewQuestion> {
    const response = await apiClient.patch<InterviewQuestion>(
      `/vacancies/${vacancyId}/questions/${questionId}`,
      data,
    )
    return response.data
  },

  async deleteQuestion(
    vacancyId: string,
    questionId: string,
  ): Promise<void> {
    await apiClient.delete(
      `/vacancies/${vacancyId}/questions/${questionId}`,
    )
  },

  async generateQuestions(vacancyId: string): Promise<InterviewQuestion[]> {
    const response = await apiClient.post<InterviewQuestion[]>(
      `/vacancies/${vacancyId}/questions/generate`,
    )
    return response.data
  },

  // Public
  async getPublicList(params?: {
    search?: string
    location?: string
    isRemote?: boolean
  }): Promise<Vacancy[]> {
    const response = await apiClient.get<Vacancy[]>('/jobs', { params })
    return response.data
  },

  async getPublicDetail(id: string): Promise<Vacancy> {
    const response = await apiClient.get<Vacancy>(`/jobs/${id}`)
    return response.data
  },

  async getByShareToken(token: string): Promise<Vacancy> {
    const response = await apiClient.get<Vacancy>(`/jobs/share/${token}`)
    return response.data
  },
}
