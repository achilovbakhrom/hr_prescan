import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'

export const legalRoutes: RouteRecordRaw[] = [
  {
    path: '/privacy',
    name: ROUTE_NAMES.PRIVACY_POLICY,
    component: () => import('./pages/PrivacyPolicyPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/terms',
    name: ROUTE_NAMES.TERMS_OF_SERVICE,
    component: () => import('./pages/TermsOfServicePage.vue'),
    meta: { requiresAuth: false },
  },
]
