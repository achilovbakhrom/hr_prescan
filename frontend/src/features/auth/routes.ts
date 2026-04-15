import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'

export const authRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: ROUTE_NAMES.LOGIN,
    component: () => import('./pages/LoginPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: ROUTE_NAMES.REGISTER,
    component: () => import('./pages/RegisterPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/verify-email',
    name: ROUTE_NAMES.VERIFY_EMAIL,
    component: () => import('./pages/VerifyEmailPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/choose-role',
    name: ROUTE_NAMES.CHOOSE_ROLE,
    component: () => import('./pages/ChooseRolePage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/company-setup',
    name: ROUTE_NAMES.COMPANY_SETUP,
    component: () => import('./pages/CompanySetupPage.vue'),
    meta: { requiresAuth: false },
  },
]
