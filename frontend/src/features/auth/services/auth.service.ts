import { apiClient } from '@/shared/api/client'
import type {
  AcceptInvitationRequest,
  GoogleAuthResponse,
  GoogleAuthRole,
  GoogleRegisterCompanyRequest,
  GoogleRegisterCompanyResponse,
  LoginRequest,
  LoginResponse,
  PendingInvitation,
  RegisterCompanyRequest,
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

  async registerCompany(data: RegisterCompanyRequest): Promise<void> {
    await apiClient.post('/auth/company-register/', data)
  },

  async googleAuth(credential: string, role?: GoogleAuthRole): Promise<GoogleAuthResponse> {
    const payload: { credential: string; role?: GoogleAuthRole } = { credential }
    if (role) payload.role = role
    const response = await apiClient.post<GoogleAuthResponse>('/auth/google/', payload)
    return response.data
  },

  async googleRegisterCompany(
    data: GoogleRegisterCompanyRequest,
  ): Promise<GoogleRegisterCompanyResponse> {
    const response = await apiClient.post<GoogleRegisterCompanyResponse>(
      '/auth/google/register-company/',
      data,
    )
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
}
