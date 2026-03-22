import { apiClient } from './client'

export interface AIMessage {
  role: 'user' | 'assistant'
  content: string
  actions?: Array<{ tool: string; result: Record<string, unknown> }>
  timestamp: string
}

export interface FrontendAction {
  type: 'navigate' | 'clear_history'
  path?: string
}

export interface AIResponse {
  success: boolean
  message: string
  actions?: Array<{ tool: string; result: Record<string, unknown> }>
  frontendActions?: FrontendAction[]
}

export async function sendAICommand(
  message: string,
  context?: Record<string, unknown>,
): Promise<AIResponse> {
  const response = await apiClient.post<AIResponse>('/hr/ai-assistant', {
    message,
    context,
  })
  return response.data
}
