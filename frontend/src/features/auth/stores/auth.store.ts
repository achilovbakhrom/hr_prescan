import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { extractErrorMessage } from '@/shared/api/errors'
import { authService } from '../services/auth.service'
import type {
  AcceptInvitationRequest,
  User,
  AuthTokens,
  LoginRequest,
  RegisterCompanyRequest,
  RegisterRequest,
} from '../types/auth.types'

const TOKENS_KEY = 'hr_prescan_tokens'

function loadTokens(): AuthTokens | null {
  const raw = localStorage.getItem(TOKENS_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as AuthTokens
  } catch {
    localStorage.removeItem(TOKENS_KEY)
    return null
  }
}

function saveTokens(tokens: AuthTokens): void {
  localStorage.setItem(TOKENS_KEY, JSON.stringify(tokens))
}

function clearTokens(): void {
  localStorage.removeItem(TOKENS_KEY)
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const tokens = ref<AuthTokens | null>(loadTokens())
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!tokens.value?.access && !!user.value)

  async function login(data: LoginRequest): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const response = await authService.login(data)
      tokens.value = response.tokens
      user.value = response.user
      saveTokens(response.tokens)
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function googleLogin(credential: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const response = await authService.googleAuth(credential)
      tokens.value = response.tokens
      user.value = response.user
      saveTokens(response.tokens)
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function register(data: RegisterRequest): Promise<void> {
    loading.value = true
    error.value = null
    try {
      await authService.register(data)
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function logout(): Promise<void> {
    try {
      if (tokens.value?.refresh) {
        await authService.logout(tokens.value.refresh)
      }
    } finally {
      user.value = null
      tokens.value = null
      clearTokens()
    }
  }

  async function refreshAccessToken(): Promise<string | null> {
    if (!tokens.value?.refresh) return null
    try {
      const response = await authService.refreshToken(tokens.value.refresh)
      tokens.value = { ...tokens.value, access: response.access }
      saveTokens(tokens.value)
      return response.access
    } catch {
      user.value = null
      tokens.value = null
      clearTokens()
      return null
    }
  }

  async function fetchUser(): Promise<void> {
    if (!tokens.value?.access) return
    try {
      user.value = await authService.getMe()
    } catch {
      user.value = null
      tokens.value = null
      clearTokens()
    }
  }

  async function acceptInvitation(data: AcceptInvitationRequest): Promise<void> {
    loading.value = true
    error.value = null
    try {
      await authService.acceptInvitation(data)
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function registerCompany(data: RegisterCompanyRequest): Promise<void> {
    loading.value = true
    error.value = null
    try {
      await authService.registerCompany(data)
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function initAuth(): Promise<void> {
    const stored = loadTokens()
    if (!stored?.access) {
      tokens.value = null
      return
    }
    tokens.value = stored
    await fetchUser()
  }

  return {
    user,
    tokens,
    loading,
    error,
    isAuthenticated,
    login,
    googleLogin,
    register,
    logout,
    refreshAccessToken,
    acceptInvitation,
    registerCompany,
    fetchUser,
    initAuth,
  }
})
