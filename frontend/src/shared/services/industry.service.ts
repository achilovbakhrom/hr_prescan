import { apiClient } from '@/shared/api/client'

export interface Industry {
  slug: string
  name: string
  nameRu?: string
  nameUz?: string
}

let cachedIndustries: Industry[] | null = null

export async function fetchIndustries(): Promise<Industry[]> {
  if (cachedIndustries) return cachedIndustries
  const { data } = await apiClient.get<Industry[]>('/public/industries')
  cachedIndustries = data
  return data
}
