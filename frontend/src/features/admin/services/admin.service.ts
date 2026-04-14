import { apiClient } from '@/shared/api/client'
import type { AdminCompany, AdminUser, PlatformAnalytics } from '../types/admin.types'
import type { SubscriptionPlan } from '@/shared/types/subscription.types'

interface PaginatedResponse<T> {
  results: T[]
  count: number
}

export const adminService = {
  async getCompanies(params?: {
    search?: string
    page?: number
  }): Promise<PaginatedResponse<AdminCompany>> {
    const response = await apiClient.get<PaginatedResponse<AdminCompany>>(
      '/admin-panel/companies',
      { params },
    )
    return response.data
  },

  async toggleCompanyStatus(id: string, isActive: boolean): Promise<AdminCompany> {
    const response = await apiClient.patch<AdminCompany>(`/admin-panel/companies/${id}`, {
      isActive,
    })
    return response.data
  },

  async getUsers(params?: {
    search?: string
    role?: string
    page?: number
  }): Promise<PaginatedResponse<AdminUser>> {
    const response = await apiClient.get<PaginatedResponse<AdminUser>>('/admin-panel/users', {
      params,
    })
    return response.data
  },

  async toggleUserStatus(id: string, isActive: boolean): Promise<AdminUser> {
    const response = await apiClient.patch<AdminUser>(`/admin-panel/users/${id}`, { isActive })
    return response.data
  },

  async getAnalytics(): Promise<PlatformAnalytics> {
    const response = await apiClient.get<PlatformAnalytics>('/admin-panel/analytics')
    return response.data
  },

  async getPlans(): Promise<SubscriptionPlan[]> {
    const response = await apiClient.get<SubscriptionPlan[]>('/admin-panel/plans')
    return response.data
  },

  async updatePlan(id: string, data: Partial<SubscriptionPlan>): Promise<SubscriptionPlan> {
    const response = await apiClient.put<SubscriptionPlan>(`/admin-panel/plans/${id}`, data)
    return response.data
  },
}
