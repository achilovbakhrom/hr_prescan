import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'

export const dashboardRoutes: RouteRecordRaw[] = [
  {
    path: '/dashboard',
    name: ROUTE_NAMES.DASHBOARD,
    component: () => import('./pages/DashboardPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/analytics',
    name: ROUTE_NAMES.HR_ANALYTICS,
    component: () => import('./pages/HRAnalyticsPage.vue'),
    meta: { requiresAuth: true, roles: ['admin', 'hr'] },
  },
]
