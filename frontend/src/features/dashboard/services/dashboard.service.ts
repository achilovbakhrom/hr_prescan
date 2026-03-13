import { apiClient } from '@/shared/api/client'
import type { DashboardStats } from '../types/dashboard.types'

export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    const { data } = await apiClient.get<DashboardStats>('/hr/dashboard/')
    return data
  },
}
