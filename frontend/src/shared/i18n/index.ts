import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import ru from './locales/ru.json'

export type MessageSchema = typeof en

const LOCALE_STORAGE_KEY = 'hr_prescan_locale'

function getDefaultLocale(): string {
  const stored = localStorage.getItem(LOCALE_STORAGE_KEY)
  if (stored === 'en' || stored === 'ru') return stored

  const browserLocale = navigator.language.split('-')[0]
  if (browserLocale === 'ru') return 'ru'

  return 'en'
}

export const i18n = createI18n<[MessageSchema], 'en' | 'ru'>({
  legacy: false,
  locale: getDefaultLocale(),
  fallbackLocale: 'en',
  messages: {
    en,
    ru,
  },
})

export function setLocale(locale: 'en' | 'ru'): void {
  i18n.global.locale.value = locale
  localStorage.setItem(LOCALE_STORAGE_KEY, locale)
  document.documentElement.lang = locale
}

export function getLocale(): string {
  return i18n.global.locale.value
}
