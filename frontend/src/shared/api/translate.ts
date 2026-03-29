import { apiClient } from './client'

export interface TranslateResponse {
  translatedText: string
  language: string
}

export async function translateContent(params: {
  model: string
  objectId: string
  field: string
  targetLanguage: string
}): Promise<TranslateResponse> {
  const response = await apiClient.post<TranslateResponse>('/hr/translate', params)
  return response.data
}

export interface BatchTranslateItem {
  id: string
  translations: Record<string, string>
}

export interface BatchTranslateResponse {
  items: BatchTranslateItem[]
  language: string
}

export async function batchTranslateItems(params: {
  vacancyId: string
  itemType: 'criteria' | 'questions'
  step: 'prescanning' | 'interview'
  targetLanguage: string
}): Promise<BatchTranslateResponse> {
  const response = await apiClient.post<BatchTranslateResponse>('/hr/translate/batch', params)
  return response.data
}
