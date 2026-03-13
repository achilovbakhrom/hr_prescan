export interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  phone: string | null
  role: UserRole
  company: Company | null
  emailVerified: boolean
}

export type UserRole = 'admin' | 'hr' | 'candidate'

export interface Company {
  id: string
  name: string
  industry: string
  size: CompanySize
  country: string
  logo: string | null
  website: string | null
}

export type CompanySize = 'small' | 'medium' | 'large' | 'enterprise'

export interface CompanyRegisterRequest {
  companyName: string
  industry: string
  size: CompanySize
  country: string
  adminEmail: string
  adminPassword: string
  adminFirstName: string
  adminLastName: string
}

export interface AcceptInvitationRequest {
  token: string
  password: string
  firstName: string
  lastName: string
}

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
