export const USER_ROLES = {
  ADMIN: 'admin',
  HR: 'hr',
  CANDIDATE: 'candidate',
} as const

export type UserRoleValue = (typeof USER_ROLES)[keyof typeof USER_ROLES]
