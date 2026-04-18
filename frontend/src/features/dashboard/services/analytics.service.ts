import { apiClient } from '@/shared/api/client'
import type { CompanyAnalytics } from '../types/analytics.types'

export const analyticsService = {
  async getCompanyAnalytics(): Promise<CompanyAnalytics> {
    const { data } = await apiClient.get<CompanyAnalytics>('/hr/analytics/')
    return data
  },
}
