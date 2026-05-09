import { initializeGoogleAnalytics } from '@/shared/analytics/googleAnalytics'
import { useThemeStore } from '@/shared/stores/theme.store'

export default defineNuxtPlugin(() => {
  useThemeStore()
  initializeGoogleAnalytics(useRouter())
})
