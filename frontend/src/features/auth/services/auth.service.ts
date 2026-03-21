import { apiClient } from '@/shared/api/client'
import type {
  AcceptInvitationRequest,
  LoginRequest,
  LoginResponse,
  PendingInvitation,
  RegisterCompanyRequest,
  RegisterRequest,
  User,
} from '../types/auth.types'

export const authService = {
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', data)
    return response.data
  },

  async register(data: RegisterRequest): Promise<User> {
    const response = await apiClient.post<User>('/auth/register', data)
    return response.data
  },

  async logout(refreshToken: string): Promise<void> {
    await apiClient.post('/auth/logout', { refresh: refreshToken })
  },

  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    const response = await apiClient.post<{ access: string }>(
      '/auth/token/refresh',
      { refresh: refreshToken },
    )
    return response.data
  },

  async verifyEmail(token: string): Promise<void> {
    await apiClient.post('/auth/verify-email', { token })
  },

  async getMe(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me')
    return response.data
  },

  async acceptInvitation(data: AcceptInvitationRequest): Promise<void> {
    await apiClient.post('/auth/accept-invitation', data)
  },

  async registerCompany(data: RegisterCompanyRequest): Promise<void> {
    await apiClient.post('/auth/company-register', data)
  },

  async googleAuth(credential: string): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/google', { credential })
    return response.data
  },

  async getMyInvitations(): Promise<PendingInvitation[]> {
    const response = await apiClient.get<PendingInvitation[]>('/auth/my-invitations')
    return response.data
  },

  async acceptCompanyInvitation(token: string): Promise<{ user: User }> {
    const response = await apiClient.post<{ user: User }>('/auth/accept-company-invitation', { token })
    return response.data
  },
}
