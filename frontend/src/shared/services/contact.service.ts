import { apiClient } from '@/shared/api/client'

export interface ContactPayload {
  name: string
  email: string
  subject?: string
  message: string
}

export const contactService = {
  /** Send a public contact-form message to the support inbox. */
  async send(payload: ContactPayload): Promise<void> {
    await apiClient.post('/public/contact/', payload)
  },
}
