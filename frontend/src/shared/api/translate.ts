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
