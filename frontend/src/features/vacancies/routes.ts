import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { USER_ROLES } from '@/shared/constants/roles'

export const vacancyRoutes: RouteRecordRaw[] = [
  {
    path: '/vacancies',
    name: ROUTE_NAMES.VACANCY_LIST,
    component: () => import('./pages/VacancyListPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
  },
  {
    path: '/vacancies/create',
    name: ROUTE_NAMES.VACANCY_CREATE,
    component: () => import('./pages/VacancyCreatePage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
  },
  {
    path: '/vacancies/:id',
    name: ROUTE_NAMES.VACANCY_DETAIL,
    component: () => import('./pages/VacancyDetailPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
  },
]

export const publicVacancyRoutes: RouteRecordRaw[] = [
  {
    path: '/jobs',
    name: ROUTE_NAMES.JOB_BOARD,
    component: () => import('./pages/PublicJobBoardPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/jobs/:id',
    name: ROUTE_NAMES.JOB_DETAIL,
    component: () => import('./pages/PublicVacancyDetailPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/jobs/share/:token',
    name: ROUTE_NAMES.JOB_SHARE,
    component: () => import('./pages/PublicVacancyDetailPage.vue'),
    meta: { requiresAuth: false },
  },
]
