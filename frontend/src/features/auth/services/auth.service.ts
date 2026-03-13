import { apiClient } from '@/shared/api/client'
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  CompanyRegisterRequest,
  AcceptInvitationRequest,
  User,
  Company,
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

  async registerCompany(
    data: CompanyRegisterRequest,
  ): Promise<{ company: Company; user: User }> {
    const response = await apiClient.post<{ company: Company; user: User }>(
      '/auth/register-company',
      data,
    )
    return response.data
  },

  async acceptInvitation(data: AcceptInvitationRequest): Promise<User> {
    const response = await apiClient.post<User>(
      '/auth/accept-invitation',
      data,
    )
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
}
