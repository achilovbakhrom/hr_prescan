export const SUPPORTED_LOCALES = [
  'en',
  'ru',
  'uz',
  'kk',
  'tr',
  'ar',
  'es',
  'fr',
  'de',
  'uk',
] as const

export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number]

export interface LocaleOption {
  code: SupportedLocale
  label: string
  flag: string
}

export const LOCALE_STORAGE_KEY = 'hr_prescan_locale'

export const LOCALE_OPTIONS: LocaleOption[] = [
  { code: 'en', label: 'English', flag: '🇺🇸' },
  { code: 'ru', label: 'Русский', flag: '🇷🇺' },
  { code: 'uz', label: "O'zbekcha", flag: '🇺🇿' },
  { code: 'kk', label: 'Қазақша', flag: '🇰🇿' },
  { code: 'tr', label: 'Türkçe', flag: '🇹🇷' },
  { code: 'ar', label: 'العربية', flag: '🇸🇦' },
  { code: 'es', label: 'Español', flag: '🇪🇸' },
  { code: 'fr', label: 'Français', flag: '🇫🇷' },
  { code: 'de', label: 'Deutsch', flag: '🇩🇪' },
  { code: 'uk', label: 'Українська', flag: '🇺🇦' },
]

export const PRESCANNING_LANGUAGE_OPTIONS = LOCALE_OPTIONS.map(({ code, label }) => ({
  value: code,
  label,
}))

export function isSupportedLocale(value: unknown): value is SupportedLocale {
  return typeof value === 'string' && SUPPORTED_LOCALES.includes(value as SupportedLocale)
}

export function normalizeLocale(value: string | null | undefined): SupportedLocale | null {
  if (!value) return null
  const normalized = value.toLowerCase().replace('_', '-')
  const exact = normalized.split(';', 1)[0]
  if (isSupportedLocale(exact)) return exact

  const base = exact.split('-', 1)[0]
  return isSupportedLocale(base) ? base : null
}
