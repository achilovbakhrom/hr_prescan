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

// ---------- Google OAuth ----------

export type GoogleAuthRole = 'candidate' | 'hr'

export interface GoogleAuthTokensResponse {
  tokens: AuthTokens
  user: User
}

// Backend returns snake_case but the axios client has a response interceptor
// that converts keys to camelCase before they reach callers.
export interface GoogleAuthNeedsRoleResponse {
  needsRole: true
  email: string
  firstName: string
  lastName: string
}

export interface GoogleAuthNeedsCompanyResponse {
  needsCompany: true
  email: string
  firstName: string
  lastName: string
}

export type GoogleAuthResponse =
  | GoogleAuthTokensResponse
  | GoogleAuthNeedsRoleResponse
  | GoogleAuthNeedsCompanyResponse

export function isGoogleTokensResponse(
  response: GoogleAuthResponse,
): response is GoogleAuthTokensResponse {
  return 'tokens' in response
}

export function isGoogleNeedsRoleResponse(
  response: GoogleAuthResponse,
): response is GoogleAuthNeedsRoleResponse {
  return 'needsRole' in response && response.needsRole === true
}

export function isGoogleNeedsCompanyResponse(
  response: GoogleAuthResponse,
): response is GoogleAuthNeedsCompanyResponse {
  return 'needsCompany' in response && response.needsCompany === true
}
