// Re-export shared types so intra-feature imports still work
export type {
  User,
  Company,
  CompanySize,
  UserRole,
  PendingInvitation,
} from '@/shared/types/auth.types'

// Import shared types needed by feature-specific interfaces
import type { User } from '@/shared/types/auth.types'

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  firstName: string
  lastName: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface LoginResponse {
  tokens: AuthTokens
  user: User
}

export interface AcceptInvitationRequest {
  token: string
  password: string
  firstName: string
  lastName: string
}
