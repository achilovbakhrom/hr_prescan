import { initializeGoogleAnalytics } from '@/shared/analytics/googleAnalytics'
import { useThemeStore } from '@/shared/stores/theme.store'

export default defineNuxtPlugin(() => {
  const themeStore = useThemeStore()
  useNuxtApp().hook('app:mounted', () => {
    window.setTimeout(() => {
      themeStore.hydratePreferences()
    }, 100)
  })
  initializeGoogleAnalytics(useRouter())
})
