import type { RouteRecordRaw } from 'vue-router'
import { ROUTE_NAMES } from '@/shared/constants/routes'

export const landingRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    name: ROUTE_NAMES.LANDING,
    component: () => import('./pages/LandingPage.vue'),
    meta: {
      requiresAuth: false,
      seo: {
        title: 'PreScreen AI - AI-Powered Candidate Screening',
        description:
          'Automate candidate prescreening with AI interviews, multilingual vacancy workflows, and structured hiring insights.',
        path: '/',
      },
    },
  },
]
