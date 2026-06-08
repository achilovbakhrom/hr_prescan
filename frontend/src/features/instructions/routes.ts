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

// Public version of the same guide, reachable from the landing page (rendered
// in the public layout, no auth required).
export const publicInstructionsRoutes: RouteRecordRaw[] = [
  {
    path: '/guide',
    name: ROUTE_NAMES.GUIDE,
    component: () => import('./pages/InstructionsPage.vue'),
    meta: {
      requiresAuth: false,
      seo: {
        title: 'How it works | PreScreen AI',
        description:
          'A step-by-step guide to PreScreen AI — create a vacancy, set up AI pre-screening and interviews, review scored candidates, and what applicants experience.',
        path: '/guide',
      },
    },
  },
]
