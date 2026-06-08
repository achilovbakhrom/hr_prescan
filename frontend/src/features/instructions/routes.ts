import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'

export const instructionsRoutes: RouteRecordRaw[] = [
  {
    path: '/instructions',
    name: ROUTE_NAMES.INSTRUCTIONS,
    component: () => import('./pages/InstructionsPage.vue'),
    meta: {
      requiresAuth: true,
      roles: ['admin', 'hr'],
    },
  },
]
