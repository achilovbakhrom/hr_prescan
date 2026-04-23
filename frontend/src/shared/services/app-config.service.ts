import { apiClient } from '@/shared/api/client'

export interface PublicAppConfig {
  telegramHrBotUsername: string
  telegramCandidateBotUsername: string
}

let publicConfigPromise: Promise<PublicAppConfig> | null = null

export const appConfigService = {
  async getPublicConfig(): Promise<PublicAppConfig> {
    if (!publicConfigPromise) {
      publicConfigPromise = apiClient
        .get<PublicAppConfig>('/public/app-config')
        .then((response) => response.data)
        .catch((error) => {
          publicConfigPromise = null
          throw error
        })
    }

    return publicConfigPromise
  },
}
