import { apiClient } from '@/shared/api/client'

export type UILocale = 'en' | 'ru' | 'uz'

export interface Language {
  code: string
  name: string
  nameRu: string
  nameUz: string
}

let cachedLanguages: Language[] | null = null

export async function fetchLanguages(): Promise<Language[]> {
  if (cachedLanguages) return cachedLanguages
  const { data } = await apiClient.get<Language[]>('/public/languages')
  cachedLanguages = data
  return data
}

export async function detectLanguage(): Promise<UILocale> {
  const { data } = await apiClient.get<{ language: UILocale }>('/public/detect-language')
  return data.language
}

export async function saveUserLanguage(lang: UILocale): Promise<void> {
  await apiClient.patch('/auth/me/', { language: lang })
}
