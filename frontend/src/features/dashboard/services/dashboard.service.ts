import { apiClient } from '@/shared/api/client'
import type { DashboardStats, CandidateDashboardStats } from '../types/dashboard.types'

export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    const { data } = await apiClient.get<DashboardStats>('/hr/dashboard/')
    return data
  },

  async getCandidateStats(): Promise<CandidateDashboardStats> {
    const { data } = await apiClient.get<CandidateDashboardStats>('/candidate/dashboard/')
    return data
  },
}
