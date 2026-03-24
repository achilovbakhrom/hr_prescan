import { apiClient } from '@/shared/api/client'

export interface Country {
  code: string
  name: string
}

let cachedCountries: Country[] | null = null

export async function fetchCountries(): Promise<Country[]> {
  if (cachedCountries) return cachedCountries
  const { data } = await apiClient.get<Country[]>('/public/countries')
  cachedCountries = data
  return data
}
