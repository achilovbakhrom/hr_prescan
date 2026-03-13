import { apiClient } from '@/shared/api/client'
import type { Company } from '@/features/auth/types/auth.types'
import type {
  CompanyProfileUpdate,
  Invitation,
  TeamMember,
  InviteHRRequest,
} from '../types/settings.types'

export const settingsService = {
  async getCompanyProfile(): Promise<Company> {
    const response = await apiClient.get<Company>('/company/profile')
    return response.data
  },

  async updateCompanyProfile(data: CompanyProfileUpdate): Promise<Company> {
    const response = await apiClient.put<Company>('/company/profile', data)
    return response.data
  },

  async inviteHR(data: InviteHRRequest): Promise<Invitation> {
    const response = await apiClient.post<Invitation>(
      '/company/invitations',
      data,
    )
    return response.data
  },

  async getTeam(): Promise<TeamMember[]> {
    const response = await apiClient.get<TeamMember[]>('/company/team')
    return response.data
  },

  async getInvitations(): Promise<Invitation[]> {
    const response = await apiClient.get<Invitation[]>(
      '/company/invitations',
    )
    return response.data
  },

  async updateTeamMember(
    userId: string,
    data: { isActive: boolean },
  ): Promise<TeamMember> {
    const response = await apiClient.patch<TeamMember>(
      `/company/team/${userId}`,
      data,
    )
    return response.data
  },
}
