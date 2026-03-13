import type { CompanySize, UserRole, User } from '@/features/auth/types/auth.types'

export interface CompanyProfileUpdate {
  name: string
  industry: string
  size: CompanySize
  country: string
  website: string | null
  description: string | null
}

export interface Invitation {
  id: string
  email: string
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
  isActive: boolean
  createdAt: string
}

export interface InviteHRRequest {
  email: string
}
