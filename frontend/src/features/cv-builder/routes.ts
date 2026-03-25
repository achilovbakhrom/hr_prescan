import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { USER_ROLES } from '@/shared/constants/roles'

export const cvBuilderRoutes: RouteRecordRaw[] = [
  {
    path: '/cv-builder',
    name: ROUTE_NAMES.CV_BUILDER,
    component: () => import('./pages/CvBuilderPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.CANDIDATE] },
  },
]
