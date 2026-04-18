import { getLocale } from '@/shared/i18n'

interface Translatable {
  name: string
  nameRu?: string
  nameUz?: string
}

/**
 * Returns the translated name based on the current locale.
 * Works outside of setup() by reading from the i18n instance directly.
 */
export function getTranslatedName(item: Translatable): string {
  const locale = getLocale()
  if (locale === 'ru' && item.nameRu) return item.nameRu
  if (locale === 'uz' && item.nameUz) return item.nameUz
  return item.name
}

/**
 * Returns true if the query matches any of the item's translated names.
 */
export function matchesTranslatedName(item: Translatable, query: string): boolean {
  const q = query.toLowerCase()
  if (item.name.toLowerCase().includes(q)) return true
  if (item.nameRu && item.nameRu.toLowerCase().includes(q)) return true
  if (item.nameUz && item.nameUz.toLowerCase().includes(q)) return true
  return false
}
