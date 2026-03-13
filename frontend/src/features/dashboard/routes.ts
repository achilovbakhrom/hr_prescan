import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'

export const dashboardRoutes: RouteRecordRaw[] = [
  {
    path: '/dashboard',
    name: ROUTE_NAMES.DASHBOARD,
    component: () => import('./pages/DashboardPage.vue'),
    meta: { requiresAuth: true },
  },
]
