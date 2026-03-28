export type HRPermission =
  | 'manage_vacancies'
  | 'manage_candidates'
  | 'manage_interviews'
  | 'manage_team'
  | 'view_analytics'
  | 'manage_settings'

export const HR_PERMISSIONS = {
  MANAGE_VACANCIES: 'manage_vacancies' as HRPermission,
  MANAGE_CANDIDATES: 'manage_candidates' as HRPermission,
  MANAGE_INTERVIEWS: 'manage_interviews' as HRPermission,
  MANAGE_TEAM: 'manage_team' as HRPermission,
  VIEW_ANALYTICS: 'view_analytics' as HRPermission,
  MANAGE_SETTINGS: 'manage_settings' as HRPermission,
}

export const ALL_HR_PERMISSIONS: HRPermission[] = Object.values(HR_PERMISSIONS)

export interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  phone: string | null
  role: UserRole
  hrPermissions: HRPermission[]
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

export interface CompanyMembership {
  company: Company
  role: UserRole
  hrPermissions: HRPermission[]
  createdAt: string
}
