import { apiClient } from '@/shared/api/client'

export interface EducationLevel {
  slug: string
  name: string
  order: number
}

let cachedEducationLevels: EducationLevel[] | null = null

export async function fetchEducationLevels(): Promise<EducationLevel[]> {
  if (cachedEducationLevels) return cachedEducationLevels
  const { data } = await apiClient.get<EducationLevel[]>('/public/education-levels')
  cachedEducationLevels = data
  return data
}
