import type { HRPermission, User, UserRole } from '@/shared/types/auth.types'

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
