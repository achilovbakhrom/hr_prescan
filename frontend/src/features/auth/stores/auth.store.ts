import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { extractErrorMessage } from '@/shared/api/errors'
import { authService } from '../services/auth.service'
import type { CompanyMembership } from '@/shared/types/auth.types'
import type {
  AcceptInvitationRequest,
  CompleteCompanySetupRequest,
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
  const companies = ref<CompanyMembership[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!tokens.value?.access && !!user.value)
  const hasMultipleCompanies = computed(() => companies.value.length > 1)

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

  async function telegramLogin(data: { tokens: AuthTokens; user: User }): Promise<void> {
    tokens.value = data.tokens
    user.value = data.user
    saveTokens(data.tokens)
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

  async function completeCompanySetup(data: CompleteCompanySetupRequest): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const response = await authService.completeCompanySetup(data)
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

  async function completeOnboarding(): Promise<void> {
    loading.value = true
    try {
      const response = await authService.completeOnboarding()
      user.value = response.user
    } finally {
      loading.value = false
    }
  }

  async function fetchCompanies(): Promise<void> {
    try {
      companies.value = await authService.getMyCompanies()
    } catch {
      companies.value = []
    }
  }

  async function switchCompany(companyId: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      user.value = await authService.switchCompany(companyId)
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
    if (user.value) {
      await fetchCompanies()
    }
  }

  return {
    user,
    tokens,
    companies,
    loading,
    error,
    isAuthenticated,
    hasMultipleCompanies,
    login,
    googleLogin,
    telegramLogin,
    register,
    logout,
    refreshAccessToken,
    acceptInvitation,
    registerCompany,
    completeCompanySetup,
    completeOnboarding,
    fetchUser,
    fetchCompanies,
    switchCompany,
    initAuth,
  }
})
