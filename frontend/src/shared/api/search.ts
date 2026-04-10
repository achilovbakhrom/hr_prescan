import { apiClient } from './client'

export interface SearchVacancy {
  id: string
  title: string
  status: string
}

export interface SearchCandidate {
  id: string
  candidateName: string
  candidateEmail: string
  status: string
  vacancyTitle: string
}

export interface SearchResults {
  vacancies: SearchVacancy[]
  candidates: SearchCandidate[]
}

export async function globalSearch(q: string): Promise<SearchResults> {
  const response = await apiClient.get<SearchResults>('/hr/search', {
    params: { q },
  })
  return response.data
}
