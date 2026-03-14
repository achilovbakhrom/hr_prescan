import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'

export const errorRoutes: RouteRecordRaw[] = [
  {
    path: '/403',
    name: ROUTE_NAMES.FORBIDDEN,
    component: () => import('./pages/ForbiddenPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/500',
    name: ROUTE_NAMES.SERVER_ERROR,
    component: () => import('./pages/ServerErrorPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/:pathMatch(.*)*',
    name: ROUTE_NAMES.NOT_FOUND,
    component: () => import('./pages/NotFoundPage.vue'),
    meta: { requiresAuth: false },
  },
]
