import { initializeGoogleAnalytics } from '@/shared/analytics/googleAnalytics'
import { useThemeStore } from '@/shared/stores/theme.store'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'

async function enforceInitialRouteAccess(): Promise<void> {
  const router = useRouter()
  const route = router.currentRoute.value
  const authStore = useAuthStore()

  if (!authStore.user && authStore.tokens) {
    await authStore.initAuth()
  }

  const requiresAuth = route.meta.requiresAuth !== false
  if (requiresAuth && !authStore.isAuthenticated) {
    await navigateTo(
      { name: ROUTE_NAMES.LOGIN, query: { redirect: route.fullPath } },
      { replace: true },
    )
    return
  }

  const isAuthPage = route.name === ROUTE_NAMES.LOGIN || route.name === ROUTE_NAMES.REGISTER
  if (isAuthPage && authStore.isAuthenticated) {
    await navigateTo({ name: ROUTE_NAMES.DASHBOARD }, { replace: true })
    return
  }

  if (
    authStore.isAuthenticated &&
    authStore.user?.onboardingCompleted === false &&
    route.name !== ROUTE_NAMES.CHOOSE_ROLE
  ) {
    await navigateTo({ name: ROUTE_NAMES.CHOOSE_ROLE }, { replace: true })
    return
  }

  if (
    authStore.isAuthenticated &&
    authStore.user?.onboardingCompleted === true &&
    authStore.activeMode === 'hr' &&
    authStore.currentAccessRole !== 'candidate' &&
    !authStore.user.company &&
    route.name !== ROUTE_NAMES.COMPANY_SETUP
  ) {
    await navigateTo({ name: ROUTE_NAMES.COMPANY_SETUP }, { replace: true })
    return
  }

  const allowedRoles = route.meta.roles as string[] | undefined
  const accessRole = authStore.currentAccessRole
  if (allowedRoles && accessRole && !allowedRoles.includes(accessRole)) {
    await navigateTo({ name: ROUTE_NAMES.FORBIDDEN }, { replace: true })
  }
}

export default defineNuxtPlugin(() => {
  const themeStore = useThemeStore()
  useNuxtApp().hook('app:mounted', () => {
    window.setTimeout(() => {
      themeStore.hydratePreferences()
    }, 100)
    void enforceInitialRouteAccess()
  })
  initializeGoogleAnalytics(useRouter())
})
