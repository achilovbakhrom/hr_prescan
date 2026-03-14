import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'

export const notificationRoutes: RouteRecordRaw[] = [
  {
    path: '/notifications',
    name: ROUTE_NAMES.NOTIFICATIONS,
    component: () => import('./pages/NotificationsPage.vue'),
    meta: { requiresAuth: true },
  },
]
