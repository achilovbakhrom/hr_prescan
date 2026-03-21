import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { USER_ROLES } from '@/shared/constants/roles'

export const settingsRoutes: RouteRecordRaw[] = [
  {
    path: '/profile',
    name: ROUTE_NAMES.PROFILE,
    component: () => import('./pages/ProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings/company',
    name: ROUTE_NAMES.COMPANY_PROFILE,
    component: () => import('./pages/CompanyProfilePage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
  },
  {
    path: '/settings/team',
    name: ROUTE_NAMES.TEAM_MANAGEMENT,
    component: () => import('./pages/TeamManagementPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN] },
  },
]
