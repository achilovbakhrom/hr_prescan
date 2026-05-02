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
  shareToken?: string
  /** Use `/translate/` (any auth) instead of `/hr/translate/` (HR-only). */
  scope?: 'hr' | 'public'
}): Promise<TranslateResponse> {
  const endpoint = params.scope === 'public' ? '/translate/' : '/hr/translate/'
  const { scope: _scope, ...body } = params
  void _scope
  const response = await apiClient.post<TranslateResponse>(endpoint, body)
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
  const response = await apiClient.post<BatchTranslateResponse>('/hr/translate/batch/', params)
  return response.data
}
