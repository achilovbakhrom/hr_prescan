import { apiClient } from '@/shared/api/client'
import type { Invitation, InviteHRRequest, TeamMember } from '../types/settings.types'

export const settingsService = {
  async inviteHR(data: InviteHRRequest): Promise<Invitation> {
    const response = await apiClient.post<{ invitation: Invitation }>('/hr/company/invite', data)
    return response.data.invitation
  },

  async getTeam(): Promise<TeamMember[]> {
    const response = await apiClient.get<TeamMember[]>('/hr/company/team')
    return response.data
  },

  async getInvitations(): Promise<Invitation[]> {
    const response = await apiClient.get<Invitation[]>('/hr/company/invite')
    return response.data
  },

  async cancelInvitation(invitationId: string): Promise<void> {
    await apiClient.delete('/hr/company/invite', {
      data: { invitationId },
    })
  },

  async updateTeamMember(
    userId: string,
    data: { isActive?: boolean; hrPermissions?: string[] },
  ): Promise<TeamMember> {
    const response = await apiClient.patch<TeamMember>(`/hr/company/team/${userId}`, data)
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
