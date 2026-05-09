import { createI18n } from 'vue-i18n'
import type { WritableComputedRef } from 'vue'
import en from './locales/en.json'
import ru from './locales/ru.json'
import uz from './locales/uz.json'
import kk from './locales/kk.json'
import tr from './locales/tr.json'
import ar from './locales/ar.json'
import es from './locales/es.json'
import fr from './locales/fr.json'
import de from './locales/de.json'
import {
  LOCALE_STORAGE_KEY,
  SUPPORTED_LOCALES,
  isSupportedLocale,
  normalizeLocale,
  type SupportedLocale,
} from './supportedLocales'

export type MessageSchema = typeof en

const dateFormat = {
  short: {
    year: 'numeric' as const,
    month: 'short' as const,
    day: 'numeric' as const,
  },
  long: {
    year: 'numeric' as const,
    month: 'long' as const,
    day: 'numeric' as const,
    hour: '2-digit' as const,
    minute: '2-digit' as const,
  },
}

const currencyByLocale: Record<SupportedLocale, string> = {
  en: 'USD',
  ru: 'RUB',
  uz: 'UZS',
  kk: 'KZT',
  tr: 'TRY',
  ar: 'USD',
  es: 'EUR',
  fr: 'EUR',
  de: 'EUR',
}

const datetimeFormats = Object.fromEntries(
  SUPPORTED_LOCALES.map((locale) => [locale, dateFormat]),
) as Record<SupportedLocale, typeof dateFormat>

const numberFormats = Object.fromEntries(
  SUPPORTED_LOCALES.map((locale) => [
    locale,
    {
      currency: {
        style: 'currency' as const,
        currency: currencyByLocale[locale],
      },
      decimal: {
        style: 'decimal' as const,
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
      },
      percent: {
        style: 'percent' as const,
        minimumFractionDigits: 0,
        maximumFractionDigits: 1,
      },
    },
  ]),
) as unknown as Record<SupportedLocale, Record<string, Intl.NumberFormatOptions>>

function getStoredLocale(): SupportedLocale | null {
  if (typeof localStorage === 'undefined') return null
  return normalizeLocale(localStorage.getItem(LOCALE_STORAGE_KEY))
}

export function getBrowserLocale(): SupportedLocale {
  if (typeof navigator === 'undefined') return 'en'
  const candidates = [...(navigator.languages ?? []), navigator.language]
  for (const candidate of candidates) {
    const locale = normalizeLocale(candidate)
    if (locale) return locale
  }
  return 'en'
}

function getDefaultLocale(): SupportedLocale {
  return getStoredLocale() ?? getBrowserLocale()
}

function applyDocumentLocale(locale: SupportedLocale): void {
  if (typeof document === 'undefined') return
  document.documentElement.lang = locale
  document.documentElement.dir = locale === 'ar' ? 'rtl' : 'ltr'
}

export function getRequestLocale(): SupportedLocale {
  return getDefaultLocale()
}

const initialLocale = getDefaultLocale()
applyDocumentLocale(initialLocale)

export const i18n = createI18n<[MessageSchema], SupportedLocale>({
  legacy: false,
  locale: initialLocale,
  fallbackLocale: 'en',
  messages: {
    en,
    ru,
    uz,
    kk,
    tr,
    ar,
    es,
    fr,
    de,
  },
  datetimeFormats,
  numberFormats,
})

export function setLocale(locale: SupportedLocale): void {
  // vue-i18n Composition mode exposes locale as a WritableComputedRef but types it as string
  ;(i18n.global.locale as unknown as WritableComputedRef<string>).value = locale
  if (typeof localStorage !== 'undefined') localStorage.setItem(LOCALE_STORAGE_KEY, locale)
  applyDocumentLocale(locale)
}

export function getLocale(): SupportedLocale {
  // vue-i18n Composition mode exposes locale as a WritableComputedRef but types it as string
  const locale =
    (i18n.global.locale as unknown as WritableComputedRef<string>).value ?? i18n.global.locale
  return isSupportedLocale(locale) ? locale : 'en'
}

export async function detectAndApplyLocale(): Promise<void> {
  if (getStoredLocale()) return
  const browserLocale = getBrowserLocale()
  ;(i18n.global.locale as unknown as WritableComputedRef<string>).value = browserLocale
  applyDocumentLocale(browserLocale)

  try {
    const { detectLanguage } = await import('@/shared/services/language.service')
    const detected = await detectLanguage()
    if (SUPPORTED_LOCALES.includes(detected)) {
      ;(i18n.global.locale as unknown as WritableComputedRef<string>).value = detected
      applyDocumentLocale(detected)
    }
  } catch (err) {
    console.warn('[i18n] language detection failed', err)
  }
}

export type { SupportedLocale }
