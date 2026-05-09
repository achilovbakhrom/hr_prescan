import { initializeGoogleAnalytics } from '@/shared/analytics/googleAnalytics'
import { useThemeStore } from '@/shared/stores/theme.store'

export default defineNuxtPlugin(() => {
  const themeStore = useThemeStore()
  useNuxtApp().hook('app:mounted', () => {
    themeStore.hydratePreferences()
  })
  initializeGoogleAnalytics(useRouter())
})
