import { ROUTE_NAMES } from '@/shared/constants/routes'
import { useAuthStore } from '@/features/auth/stores/auth.store'

export default defineNuxtRouteMiddleware(async (to) => {
  const requiresAuth = to.meta.requiresAuth !== false

  if (import.meta.server) {
    // Auth tokens are stored in localStorage, so the server cannot know whether
    // a protected route reload is authenticated. Let the client perform the
    // redirect after hydrating the auth store; this keeps app routes in the app
    // layout instead of briefly rendering the public login layout.
    return
  }

  const authStore = useAuthStore()
  if (!authStore.user && authStore.tokens) {
    await authStore.initAuth()
  }

  if (requiresAuth && !authStore.isAuthenticated) {
    return navigateTo({ name: ROUTE_NAMES.LOGIN, query: { redirect: to.fullPath } })
  }

  const isAuthPage = to.name === ROUTE_NAMES.LOGIN || to.name === ROUTE_NAMES.REGISTER
  if (isAuthPage && authStore.isAuthenticated) {
    return navigateTo({ name: ROUTE_NAMES.DASHBOARD })
  }

  if (
    authStore.isAuthenticated &&
    authStore.user?.onboardingCompleted === false &&
    to.name !== ROUTE_NAMES.CHOOSE_ROLE
  ) {
    return navigateTo({ name: ROUTE_NAMES.CHOOSE_ROLE })
  }

  if (
    authStore.isAuthenticated &&
    authStore.user?.onboardingCompleted === true &&
    authStore.user.role === 'hr' &&
    !authStore.user.company &&
    to.name !== ROUTE_NAMES.COMPANY_SETUP
  ) {
    return navigateTo({ name: ROUTE_NAMES.COMPANY_SETUP })
  }

  const allowedRoles = to.meta.roles as string[] | undefined
  if (allowedRoles && authStore.user && !allowedRoles.includes(authStore.user.role)) {
    return navigateTo({ name: ROUTE_NAMES.FORBIDDEN })
  }
})
