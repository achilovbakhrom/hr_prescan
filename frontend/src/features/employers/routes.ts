import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { USER_ROLES } from '@/shared/constants/roles'

export const employerRoutes: RouteRecordRaw[] = [
  {
    path: '/employers',
    name: ROUTE_NAMES.EMPLOYER_LIST,
    component: () => import('./pages/EmployerListPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
  },
  {
    path: '/employers/create',
    name: ROUTE_NAMES.EMPLOYER_CREATE,
    component: () => import('./pages/EmployerCreatePage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
  },
  {
    path: '/employers/:id',
    name: ROUTE_NAMES.EMPLOYER_DETAIL,
    component: () => import('./pages/EmployerDetailPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
  },
]
