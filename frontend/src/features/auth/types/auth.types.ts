// Re-export shared types so intra-feature imports still work
export type {
  User,
  Company,
  CompanySize,
  UserRole,
  PendingInvitation,
} from '@/shared/types/auth.types'

// Import shared types needed by feature-specific interfaces
import type { User, CompanySize, Company } from '@/shared/types/auth.types'

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

export interface RegisterCompanyRequest {
  companyName: string
  industry: string
  size: CompanySize
  country: string
  adminEmail: string
  adminPassword: string
  adminFirstName: string
  adminLastName: string
}

export type GoogleAuthRole = 'candidate' | 'hr'

export interface GoogleAuthTokensResponse {
  tokens: AuthTokens
  user: User
}

// Backend returns snake_case (needs_role, first_name, last_name), but the
// axios client has a global response interceptor that converts snake_case →
// camelCase before it reaches callers. So the shapes below use camelCase.
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

export interface GoogleRegisterCompanyRequest {
  credential: string
  companyName: string
  industry: string
  size: CompanySize
  country: string
  website?: string
  description?: string
}

export interface GoogleRegisterCompanyResponse {
  tokens: AuthTokens
  company: Company
  user: User
}
