import { apiClient } from '@/shared/api/client'
import type { Vacancy } from '../types/vacancy.types'

interface PublicVacancyFilters {
  search?: string
  location?: string
  isRemote?: boolean
  employmentType?: string
  experienceLevel?: string
  salaryMin?: number
  salaryMax?: number
}

interface PublicVacancyPageParams extends PublicVacancyFilters {
  page: number
  pageSize: number
}

export interface PublicVacancyPage {
  results: Vacancy[]
  count: number
  next: string | null
  previous: string | null
}

export const publicVacancyService = {
  async getPublicList(params?: PublicVacancyFilters): Promise<Vacancy[]> {
    const response = await apiClient.get<Vacancy[]>('/public/vacancies/', { params })
    return response.data
  },

  async getPublicListPage(
    params: PublicVacancyPageParams,
    signal?: AbortSignal,
  ): Promise<PublicVacancyPage> {
    const response = await apiClient.get<PublicVacancyPage>('/public/vacancies/', {
      params,
      signal,
    })
    return response.data
  },

  async getPublicDetail(id: string): Promise<Vacancy> {
    const response = await apiClient.get<Vacancy>(`/public/vacancies/${id}/`)
    return response.data
  },

  async getByShareToken(token: string): Promise<Vacancy> {
    const response = await apiClient.get<Vacancy>(`/public/vacancies/share/${token}/`)
    return response.data
  },
}
