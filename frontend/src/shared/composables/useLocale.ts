import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { setLocale, getLocale } from '@/shared/i18n'

export type SupportedLocale = 'en' | 'ru'

export interface LocaleOption {
  code: SupportedLocale
  label: string
  flag: string
}

export const LOCALE_OPTIONS: LocaleOption[] = [
  { code: 'en', label: 'English', flag: '🇺🇸' },
  { code: 'ru', label: 'Русский', flag: '🇷🇺' },
]

export function useLocale() {
  const { t, locale } = useI18n()

  const currentLocale = computed<SupportedLocale>(() => getLocale() as SupportedLocale)

  const currentLocaleOption = computed<LocaleOption | undefined>(() =>
    LOCALE_OPTIONS.find((opt) => opt.code === currentLocale.value),
  )

  function switchLocale(code: SupportedLocale): void {
    setLocale(code)
  }

  function toggleLocale(): void {
    const next = currentLocale.value === 'en' ? 'ru' : 'en'
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
