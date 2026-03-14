import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { USER_ROLES } from '@/shared/constants/roles'

export const publicSubscriptionRoutes: RouteRecordRaw[] = [
  {
    path: '/pricing',
    name: ROUTE_NAMES.PRICING,
    component: () => import('./pages/PricingPage.vue'),
    meta: { requiresAuth: false },
  },
]

export const subscriptionRoutes: RouteRecordRaw[] = [
  {
    path: '/subscription',
    name: ROUTE_NAMES.SUBSCRIPTION,
    component: () => import('./pages/SubscriptionPage.vue'),
    meta: { requiresAuth: true, roles: [USER_ROLES.ADMIN] },
  },
]
