import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { USER_ROLES } from '@/shared/constants/roles'

export const hrInterviewRoutes: RouteRecordRaw[] = [
  {
    path: '/interviews',
    name: ROUTE_NAMES.INTERVIEW_LIST,
    component: () => import('./pages/InterviewListPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
  },
  {
    path: '/interviews/:id',
    name: ROUTE_NAMES.INTERVIEW_DETAIL,
    component: () => import('./pages/InterviewDetailPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN, USER_ROLES.HR] },
  },
]

export const candidateInterviewRoutes: RouteRecordRaw[] = [
  {
    path: '/my-interview/:id',
    name: ROUTE_NAMES.CANDIDATE_INTERVIEW,
    component: () => import('./pages/CandidateInterviewPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/my-interview/:id/confirmation',
    name: ROUTE_NAMES.INTERVIEW_CONFIRMATION,
    component: () => import('./pages/InterviewConfirmationPage.vue'),
    meta: { requiresAuth: false },
  },
]

export const publicInterviewRoutes: RouteRecordRaw[] = [
  {
    path: '/interview/:token',
    name: ROUTE_NAMES.INTERVIEW_GATEWAY,
    component: () => import('./pages/InterviewGatewayPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/interview/:token/chat',
    name: ROUTE_NAMES.CHAT_INTERVIEW,
    component: () => import('./pages/ChatInterviewPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/interview/:token/room',
    name: ROUTE_NAMES.INTERVIEW_ROOM,
    component: () => import('./pages/InterviewRoomPage.vue'),
    meta: { requiresAuth: false },
  },
]
