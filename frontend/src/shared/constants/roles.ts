export const UserRole = {
  ADMIN: 'admin',
  HR_MANAGER: 'hr_manager',
  RECRUITER: 'recruiter',
  VIEWER: 'viewer',
} as const

export type UserRole = (typeof UserRole)[keyof typeof UserRole]
