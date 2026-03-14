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
import { notificationRoutes } from '@/features/notifications/routes'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { UserRole } from '@/features/auth/types/auth.types'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    roles?: UserRole[]
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  ...authRoutes,
  ...publicVacancyRoutes,
  ...publicApplicationRoutes,
  {
    path: '/',
    component: () => import('@/shared/components/AppLayout.vue'),
    children: [
      ...dashboardRoutes,
      ...vacancyRoutes,
      ...candidateRoutes,
      ...hrCandidateRoutes,
      ...notificationRoutes,
    ],
  },
]

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(async (to) => {
  const { useAuthStore } = await import('@/features/auth/stores/auth.store')
  const authStore = useAuthStore()

  if (!authStore.user && authStore.tokens) {
    await authStore.initAuth()
  }

  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    return { name: ROUTE_NAMES.LOGIN, query: { redirect: to.fullPath } }
  }

  const isAuthPage =
    to.name === ROUTE_NAMES.LOGIN || to.name === ROUTE_NAMES.REGISTER

  if (isAuthPage && authStore.isAuthenticated) {
    return { name: ROUTE_NAMES.DASHBOARD }
  }

  const allowedRoles = to.meta.roles
  if (allowedRoles && authStore.user) {
    if (!allowedRoles.includes(authStore.user.role)) {
      return { name: ROUTE_NAMES.DASHBOARD }
    }
  }

  return true
})
