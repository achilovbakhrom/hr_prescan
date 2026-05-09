import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { setLocale, getLocale, type SupportedLocale } from '@/shared/i18n'
import { LOCALE_OPTIONS } from '@/shared/i18n/supportedLocales'
import type { LocaleOption } from '@/shared/i18n/supportedLocales'

export type { SupportedLocale, LocaleOption } from '@/shared/i18n/supportedLocales'

export function useLocale() {
  const { t, locale } = useI18n()

  const currentLocale = computed<SupportedLocale>(() => getLocale() as SupportedLocale)

  const currentLocaleOption = computed<LocaleOption | undefined>(() =>
    LOCALE_OPTIONS.find((opt) => opt.code === currentLocale.value),
  )

  function switchLocale(code: SupportedLocale): void {
    setLocale(code)

    void (async () => {
      try {
        const [{ useAuthStore }, { saveUserLanguage }] = await Promise.all([
          import('@/features/auth/stores/auth.store'),
          import('@/shared/services/language.service'),
        ])
        const authStore = useAuthStore()
        if (!authStore.isAuthenticated) return
        await saveUserLanguage(code)
        if (authStore.user) authStore.user.language = code
      } catch (err) {
        console.warn('[i18n] failed to persist language', err)
      }
    })()
  }

  function toggleLocale(): void {
    const order = LOCALE_OPTIONS.map((option) => option.code)
    const idx = order.indexOf(currentLocale.value)
    const next = order[(idx + 1) % order.length]
    switchLocale(next)
  }

  return {
    t,
    locale,
    currentLocale,
    currentLocaleOption,
    localeOptions: LOCALE_OPTIONS,
    switchLocale,
    toggleLocale,
  }
}
