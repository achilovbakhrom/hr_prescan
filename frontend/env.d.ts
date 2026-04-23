/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_LIVEKIT_URL?: string
  readonly VITE_GOOGLE_CLIENT_ID?: string
  readonly VITE_TELEGRAM_BOT_USERNAME?: string
  readonly VITE_TELEGRAM_BOT_ID?: string
  readonly VITE_TELEGRAM_CANDIDATE_BOT_USERNAME?: string
  readonly VITE_TELEGRAM_HR_BOT_USERNAME?: string
  readonly VITE_BILLING_ENABLED?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
