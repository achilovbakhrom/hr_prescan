import { createI18n } from 'vue-i18n'
import type { WritableComputedRef } from 'vue'
import en from './locales/en.json'
import ru from './locales/ru.json'
import uz from './locales/uz.json'

export type MessageSchema = typeof en

const LOCALE_STORAGE_KEY = 'hr_prescan_locale'

const datetimeFormats = {
  en: {
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
  },
  ru: {
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
  },
  uz: {
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
  },
}

const numberFormats = {
  en: {
    currency: {
      style: 'currency' as const,
      currency: 'USD',
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
  ru: {
    currency: {
      style: 'currency' as const,
      currency: 'RUB',
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
  uz: {
    currency: {
      style: 'currency' as const,
      currency: 'UZS',
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
}

function getDefaultLocale(): string {
  const stored = localStorage.getItem(LOCALE_STORAGE_KEY)
  if (stored === 'en' || stored === 'ru' || stored === 'uz') return stored

  const browserLocale = navigator.language.split('-')[0]
  if (browserLocale === 'ru') return 'ru'
  if (browserLocale === 'uz') return 'uz'

  return 'en'
}

export const i18n = createI18n<[MessageSchema], 'en' | 'ru' | 'uz'>({
  legacy: false,
  locale: getDefaultLocale(),
  fallbackLocale: 'en',
  messages: {
    en,
    ru,
    uz,
  },
  datetimeFormats,
  numberFormats,
})

export function setLocale(locale: 'en' | 'ru' | 'uz'): void {
  // vue-i18n Composition mode exposes locale as a WritableComputedRef but types it as string
  ;(i18n.global.locale as unknown as WritableComputedRef<string>).value = locale
  localStorage.setItem(LOCALE_STORAGE_KEY, locale)
  document.documentElement.lang = locale
}

export function getLocale(): string {
  // vue-i18n Composition mode exposes locale as a WritableComputedRef but types it as string
  return (i18n.global.locale as unknown as WritableComputedRef<string>).value ?? i18n.global.locale
}

export async function detectAndApplyLocale(): Promise<void> {
  if (localStorage.getItem(LOCALE_STORAGE_KEY)) return
  try {
    const { detectLanguage } = await import('@/shared/services/language.service')
    const detected = await detectLanguage()
    if (detected === 'en' || detected === 'ru' || detected === 'uz') {
      setLocale(detected)
    }
  } catch (err) {
    console.warn('[i18n] language detection failed', err)
  }
}
