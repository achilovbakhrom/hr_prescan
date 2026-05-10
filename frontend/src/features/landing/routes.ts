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
        title: 'PreScreen AI - Strict AI Candidate Prescreening',
        description:
          'Add strict dynamic candidate filters, automate prescreening interviews, and let candidates complete screening by link without authentication.',
        path: '/',
      },
    },
  },
]
