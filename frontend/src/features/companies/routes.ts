import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { USER_ROLES } from '@/shared/constants/roles'

export const companyRoutes: RouteRecordRaw[] = [
  {
    path: '/companies',
    name: ROUTE_NAMES.COMPANY_LIST,
    component: () => import('./pages/CompanyListPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
  },
  {
    path: '/companies/create',
    name: ROUTE_NAMES.COMPANY_CREATE,
    component: () => import('./pages/CompanyCreatePage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
  },
  {
    path: '/companies/:id',
    name: ROUTE_NAMES.COMPANY_DETAIL,
    component: () => import('./pages/CompanyDetailPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
  },
]
