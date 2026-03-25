import { apiClient } from '@/shared/api/client'

export interface Language {
  code: string
  name: string
}

let cachedLanguages: Language[] | null = null

export async function fetchLanguages(): Promise<Language[]> {
  if (cachedLanguages) return cachedLanguages
  const { data } = await apiClient.get<Language[]>('/public/languages')
  cachedLanguages = data
  return data
}
