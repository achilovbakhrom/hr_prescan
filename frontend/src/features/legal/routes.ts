import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'

export const legalRoutes: RouteRecordRaw[] = [
  {
    path: '/privacy',
    name: ROUTE_NAMES.PRIVACY_POLICY,
    component: () => import('./pages/PrivacyPolicyPage.vue'),
    meta: {
      requiresAuth: false,
      seo: {
        title: 'Privacy Policy | PreScreen AI',
        description: 'Read how PreScreen AI handles privacy, data processing, and user data.',
        path: '/privacy',
      },
    },
  },
  {
    path: '/terms',
    name: ROUTE_NAMES.TERMS_OF_SERVICE,
    component: () => import('./pages/TermsOfServicePage.vue'),
    meta: {
      requiresAuth: false,
      seo: {
        title: 'Terms of Service | PreScreen AI',
        description: 'Review the terms that govern use of the PreScreen AI platform.',
        path: '/terms',
      },
    },
  },
]
