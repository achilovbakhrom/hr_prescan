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

export interface GoogleAuthNeedsRoleResponse {
  needs_role: true
  email: string
  first_name: string
  last_name: string
}

export interface GoogleAuthNeedsCompanyResponse {
  needs_company: true
  email: string
  first_name: string
  last_name: string
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
  return 'needs_role' in response && response.needs_role === true
}

export function isGoogleNeedsCompanyResponse(
  response: GoogleAuthResponse,
): response is GoogleAuthNeedsCompanyResponse {
  return 'needs_company' in response && response.needs_company === true
}

export interface GoogleRegisterCompanyRequest {
  credential: string
  company_name: string
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
