import type { CompanySize, HRPermission, UserRole, User } from '@/shared/types/auth.types'

export interface CompanyProfileUpdate {
  name: string
  industries: string[]
  size: CompanySize
  country: string
  website: string | null
  description: string | null
  customIndustry?: string | null
}

export interface Invitation {
  id: string
  email: string
  permissions: HRPermission[]
  invitedBy: User
  isAccepted: boolean
  expiresAt: string
  createdAt: string
}

export interface TeamMember {
  id: string
  email: string
  firstName: string
  lastName: string
  role: UserRole
  hrPermissions: HRPermission[]
  isActive: boolean
  createdAt: string
}

export interface InviteHRRequest {
  email: string
  permissions: HRPermission[]
}
