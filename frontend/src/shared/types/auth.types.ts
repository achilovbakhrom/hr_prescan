export interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  phone: string | null
  role: UserRole
  company: Company | null
  emailVerified: boolean
  onboardingCompleted: boolean
}

export type UserRole = 'admin' | 'hr' | 'candidate'

export interface Company {
  id: string
  name: string
  industries: string[]
  size: CompanySize
  country: string
  logo: string | null
  website: string | null
  subscriptionStatus?: 'trial' | 'active' | 'past_due' | 'cancelled'
  trialEndsAt?: string | null
}

export type CompanySize = 'small' | 'medium' | 'large' | 'enterprise'

export interface PendingInvitation {
  id: string
  company: Company
  invitedByName: string
  token: string
  expiresAt: string
  createdAt: string
}
