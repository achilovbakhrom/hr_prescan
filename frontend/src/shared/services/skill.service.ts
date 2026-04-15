import { apiClient } from '@/shared/api/client'

export interface Skill {
  slug: string
  name: string
  category: string
}

let cachedSkills: Skill[] | null = null

export async function fetchSkills(): Promise<Skill[]> {
  if (cachedSkills) return cachedSkills
  const { data } = await apiClient.get<Skill[]>('/public/skills')
  cachedSkills = data
  return data
}
