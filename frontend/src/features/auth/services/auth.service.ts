import { apiClient } from '@/shared/api/client'
import type { CompanyMembership } from '@/shared/types/auth.types'
import type {
  AcceptInvitationRequest,
  GoogleAuthResponse,
  GoogleAuthRole,
  LoginRequest,
  LoginResponse,
  PendingInvitation,
  RegisterRequest,
  User,
} from '../types/auth.types'

// All paths end with `/` because Django's APPEND_SLASH=True issues a
// 301 for missing trailing slashes on POST — axios then retries as GET
// and the response body is lost.
export const authService = {
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login/', data)
    return response.data
  },

  async register(data: RegisterRequest): Promise<User> {
    const response = await apiClient.post<User>('/auth/register/', data)
    return response.data
  },

  async logout(refreshToken: string): Promise<void> {
    await apiClient.post('/auth/logout/', { refresh: refreshToken })
  },

  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    const response = await apiClient.post<{ access: string }>('/auth/token/refresh/', {
      refresh: refreshToken,
    })
    return response.data
  },

  async verifyEmail(token: string): Promise<void> {
    await apiClient.post('/auth/verify-email/', { token })
  },

  async getMe(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me/')
    return response.data
  },

  async acceptInvitation(data: AcceptInvitationRequest): Promise<void> {
    await apiClient.post('/auth/accept-invitation/', data)
  },

  async googleAuth(credential: string): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/google', { credential })
    return response.data
  },

  async telegramAuth(data: {
    id: number
    first_name: string
    last_name: string
    username: string
    photo_url: string
    auth_date: number
    hash: string
  }): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/telegram/', data)
    return response.data
  },

  async getMyInvitations(): Promise<PendingInvitation[]> {
    const response = await apiClient.get<PendingInvitation[]>('/auth/my-invitations/')
    return response.data
  },

  async acceptCompanyInvitation(token: string): Promise<{ user: User }> {
    const response = await apiClient.post<{ user: User }>('/auth/accept-company-invitation/', {
      token,
    })
    return response.data
  },

  async completeOnboarding(role: 'candidate' | 'hr'): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/complete-onboarding', { role })
    return response.data
  },

  async completeCompanySetup(data: {
    company_name: string
    industries: string[]
    size: string
    country: string
    email?: string
  }): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/complete-company-setup/', data)
    return response.data
  },

  async getMyCompanies(): Promise<CompanyMembership[]> {
    const response = await apiClient.get<CompanyMembership[]>('/auth/my-companies')
    return response.data
  },

  async switchCompany(companyId: string): Promise<User> {
    const response = await apiClient.post<User>('/auth/switch-company', { companyId })
    return response.data
  },

  async switchToPersonal(): Promise<User> {
    const response = await apiClient.post<User>('/auth/switch-personal')
    return response.data
  },
}
