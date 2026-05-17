import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { USER_ROLES } from '@/shared/constants/roles'

export const candidateRoutes: RouteRecordRaw[] = [
  {
    path: '/my-applications',
    name: ROUTE_NAMES.MY_APPLICATIONS,
    component: () => import('./pages/MyApplicationsPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.CANDIDATE] },
  },
  {
    path: '/my-applications/:id',
    name: ROUTE_NAMES.MY_APPLICATION_DETAIL,
    component: () => import('./pages/MyApplicationDetailPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.CANDIDATE] },
  },
]

export const hrCandidateRoutes: RouteRecordRaw[] = [
  {
    path: '/candidate-base',
    name: ROUTE_NAMES.CANDIDATE_BASE,
    component: () => import('./pages/CandidateBasePage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
  },
  {
    path: '/candidate-base/:id',
    name: ROUTE_NAMES.CANDIDATE_BASE_DETAIL,
    component: () => import('./pages/CandidateBaseDetailPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
  },
  {
    path: '/candidates',
    name: ROUTE_NAMES.CANDIDATE_LIST,
    component: () => import('./pages/CandidateListPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
  },
  {
    path: '/candidates/:id',
    name: ROUTE_NAMES.CANDIDATE_DETAIL,
    component: () => import('./pages/CandidateDetailPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
  },
]

export const publicApplicationRoutes: RouteRecordRaw[] = [
  {
    path: '/candidate-review/:token',
    name: ROUTE_NAMES.CANDIDATE_REVIEW_SHARE,
    component: () => import('./pages/PublicCandidateReviewPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/jobs/:vacancyId/apply',
    name: ROUTE_NAMES.JOB_APPLY,
    component: () => import('./pages/ApplicationFormPage.vue'),
    meta: { requiresAuth: false },
  },
]
