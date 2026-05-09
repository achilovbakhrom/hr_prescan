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
    meta: {
      requiresAuth: false,
      seo: {
        title: 'AI Screening Jobs | PreScreen AI',
        description:
          'Browse public vacancies that use PreScreen AI for fast, structured candidate screening.',
        path: '/jobs',
      },
    },
  },
  {
    path: '/jobs/:id',
    name: ROUTE_NAMES.JOB_DETAIL,
    component: () => import('./pages/PublicVacancyDetailPage.vue'),
    meta: {
      requiresAuth: false,
      seo: {
        title: 'Job Details | PreScreen AI',
        description: 'View vacancy details and apply through PreScreen AI.',
      },
    },
  },
  {
    path: '/jobs/share/:token',
    name: ROUTE_NAMES.JOB_SHARE,
    component: () => import('./pages/PublicVacancyDetailPage.vue'),
    meta: {
      requiresAuth: false,
      seo: {
        title: 'Shared Job | PreScreen AI',
        description: 'View a shared vacancy on PreScreen AI.',
        path: '/jobs',
        noindex: true,
        robots: 'noindex, follow',
      },
    },
  },
]
