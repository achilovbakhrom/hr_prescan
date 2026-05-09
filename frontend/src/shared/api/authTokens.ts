export interface StoredAuthTokens {
  access: string
  refresh: string
}

export const AUTH_TOKENS_CHANGED_EVENT = 'hr-prescan:auth-tokens-changed'

const TOKENS_KEY = 'hr_prescan_tokens'

function notifyTokensChanged(): void {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new CustomEvent(AUTH_TOKENS_CHANGED_EVENT))
}

export function loadTokens(): StoredAuthTokens | null {
  if (typeof localStorage === 'undefined') return null
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
  if (typeof localStorage === 'undefined') return
  localStorage.setItem(TOKENS_KEY, JSON.stringify(tokens))
  notifyTokensChanged()
}

export function clearTokens(): void {
  if (typeof localStorage === 'undefined') return
  localStorage.removeItem(TOKENS_KEY)
  notifyTokensChanged()
}
