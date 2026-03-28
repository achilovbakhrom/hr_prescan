import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { authRoutes } from '@/features/auth/routes'
import { dashboardRoutes } from '@/features/dashboard/routes'
import {
  vacancyRoutes,
  publicVacancyRoutes,
} from '@/features/vacancies/routes'
import {
  candidateRoutes,
  hrCandidateRoutes,
  publicApplicationRoutes,
} from '@/features/candidates/routes'
import {
  hrInterviewRoutes,
  candidateInterviewRoutes,
  publicInterviewRoutes,
} from '@/features/interviews/routes'
import { notificationRoutes } from '@/features/notifications/routes'
import { settingsRoutes } from '@/features/settings/routes'
import {
  subscriptionRoutes,
  publicSubscriptionRoutes,
} from '@/features/subscriptions/routes'
import { cvBuilderRoutes, publicCvRoutes } from '@/features/cv-builder/routes'
import { employerRoutes } from '@/features/employers/routes'
import { landingRoutes } from '@/features/landing/routes'
import { legalRoutes } from '@/features/legal/routes'
import { errorRoutes } from '@/features/errors/routes'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { UserRole } from '@/shared/types/auth.types'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    roles?: UserRole[]
  }
}

const routes: RouteRecordRaw[] = [
  // Landing page (public, unauthenticated root)
  ...landingRoutes,

  // Public interview routes (full-screen, no layout wrapper)
  ...publicInterviewRoutes,

  // Public routes (no auth required) — with shared public header
  {
    path: '/',
    component: () => import('@/shared/components/PublicLayout.vue'),
    children: [
      ...authRoutes,
      ...publicVacancyRoutes,
      ...publicApplicationRoutes,
      ...publicSubscriptionRoutes,
      ...candidateInterviewRoutes,
      ...legalRoutes,
      ...publicCvRoutes,
    ],
  },

  // Authenticated app routes (layout wrapper)
  {
    path: '/',
    component: () => import('@/shared/components/AppLayout.vue'),
    children: [
      ...dashboardRoutes,
      ...vacancyRoutes,
      ...employerRoutes,
      ...candidateRoutes,
      ...cvBuilderRoutes,
      ...hrCandidateRoutes,
      ...hrInterviewRoutes,
      ...notificationRoutes,
      ...settingsRoutes,
      ...subscriptionRoutes,
    ],
  },

  // Error pages — catch-all must be last
  ...errorRoutes,
]

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  const { useAuthStore } = await import('@/features/auth/stores/auth.store')
  const authStore = useAuthStore()

  if (!authStore.user && authStore.tokens) {
    await authStore.initAuth()
  }

  // Pages that explicitly set requiresAuth: false skip the auth check
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    return { name: ROUTE_NAMES.LOGIN, query: { redirect: to.fullPath } }
  }

  const isAuthPage =
    to.name === ROUTE_NAMES.LOGIN ||
    to.name === ROUTE_NAMES.REGISTER ||
    to.name === ROUTE_NAMES.COMPANY_REGISTER

  if (isAuthPage && authStore.isAuthenticated) {
    return { name: ROUTE_NAMES.DASHBOARD }
  }

  // Redirect to role picker if onboarding not completed
  if (authStore.isAuthenticated && authStore.user?.onboardingCompleted === false && to.name !== ROUTE_NAMES.CHOOSE_ROLE) {
    return { name: ROUTE_NAMES.CHOOSE_ROLE }
  }

  const allowedRoles = to.meta.roles
  if (allowedRoles && authStore.user) {
    if (!allowedRoles.includes(authStore.user.role)) {
      return { name: ROUTE_NAMES.FORBIDDEN }
    }
  }

  return true
})
