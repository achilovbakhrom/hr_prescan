import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { USER_ROLES } from '@/shared/constants/roles'

export const adminRoutes: RouteRecordRaw[] = [
  {
    path: '/admin',
    name: ROUTE_NAMES.ADMIN_DASHBOARD,
    component: () => import('./pages/AdminDashboardPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN] },
  },
  {
    path: '/admin/companies',
    name: ROUTE_NAMES.ADMIN_COMPANIES,
    component: () => import('./pages/AdminCompaniesPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN] },
  },
  {
    path: '/admin/users',
    name: ROUTE_NAMES.ADMIN_USERS,
    component: () => import('./pages/AdminUsersPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN] },
  },
  {
    path: '/admin/analytics',
    name: ROUTE_NAMES.ADMIN_ANALYTICS,
    component: () => import('./pages/AdminAnalyticsPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN] },
  },
  {
    path: '/admin/plans',
    name: ROUTE_NAMES.ADMIN_PLANS,
    component: () => import('./pages/AdminPlansPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN] },
  },
]
