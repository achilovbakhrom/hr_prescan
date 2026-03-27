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
  {
    path: '/my-cvs',
    name: ROUTE_NAMES.MY_CVS,
    component: () => import('./pages/MyCvsPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.CANDIDATE] },
  },
]

export const publicCvRoutes: RouteRecordRaw[] = [
  {
    path: '/cv/:token',
    name: ROUTE_NAMES.PUBLIC_CV,
    component: () => import('./pages/PublicCvPage.vue'),
    meta: { requiresAuth: false },
  },
]
