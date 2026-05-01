export interface StoredAuthTokens {
  access: string
  refresh: string
}

export const AUTH_TOKENS_CHANGED_EVENT = 'hr-prescan:auth-tokens-changed'

const TOKENS_KEY = 'hr_prescan_tokens'

function notifyTokensChanged(): void {
  window.dispatchEvent(new CustomEvent(AUTH_TOKENS_CHANGED_EVENT))
}

export function loadTokens(): StoredAuthTokens | null {
  const raw = localStorage.getItem(TOKENS_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as StoredAuthTokens
  } catch {
    localStorage.removeItem(TOKENS_KEY)
    notifyTokensChanged()
    return null
  }
}

export function saveTokens(tokens: StoredAuthTokens): void {
  localStorage.setItem(TOKENS_KEY, JSON.stringify(tokens))
  notifyTokensChanged()
}

export function clearTokens(): void {
  localStorage.removeItem(TOKENS_KEY)
  notifyTokensChanged()
}
