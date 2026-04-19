import type { Company, HRPermission, User, UserRole } from '@/shared/types/auth.types'

export interface Invitation {
  id: string
  email: string
  companies: Company[]
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
  // Omit or empty ⇒ grant access to all companies on the inviter's account.
  companyIds?: string[]
}
