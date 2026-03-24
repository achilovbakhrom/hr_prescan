import { apiClient } from '@/shared/api/client'
import type { Company } from '@/shared/types/auth.types'
import type {
  CompanyProfileUpdate,
  Invitation,
  TeamMember,
  InviteHRRequest,
} from '../types/settings.types'

export const settingsService = {
  async getCompanyProfile(): Promise<Company> {
    const response = await apiClient.get<Company>('/hr/company/profile')
    return response.data
  },

  async updateCompanyProfile(data: CompanyProfileUpdate): Promise<Company> {
    const response = await apiClient.put<Company>(
      '/hr/company/profile',
      data,
    )
    return response.data
  },

  async inviteHR(data: InviteHRRequest): Promise<Invitation> {
    const response = await apiClient.post<Invitation>(
      '/hr/company/invite',
      data,
    )
    return response.data
  },

  async getTeam(): Promise<TeamMember[]> {
    const response = await apiClient.get<TeamMember[]>('/hr/company/team')
    return response.data
  },

  async getInvitations(): Promise<Invitation[]> {
    const response = await apiClient.get<Invitation[]>('/hr/company/invite')
    return response.data
  },

  async updateTeamMember(
    userId: string,
    data: { isActive: boolean },
  ): Promise<TeamMember> {
    const response = await apiClient.patch<TeamMember>(
      `/hr/company/team/${userId}`,
      data,
    )
    return response.data
  },

  async getTelegramStatus(): Promise<{ linked: boolean; telegramUsername: string | null }> {
    const response = await apiClient.get('/hr/telegram/status')
    return response.data
  },

  async generateTelegramLinkCode(): Promise<{ linkUrl: string; expiresAt: string }> {
    const response = await apiClient.get('/hr/telegram/link-code')
    return response.data
  },

  async unlinkTelegram(): Promise<void> {
    await apiClient.post('/hr/telegram/unlink')
  },
}
