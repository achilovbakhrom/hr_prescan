import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { extractErrorMessage } from '@/shared/api/errors'
import { setLocale } from '@/shared/i18n'
import { saveUserLanguage } from '@/shared/services/language.service'
import { authService } from '../services/auth.service'
import { loadTokens, saveTokens, clearTokens } from './auth-tokens'
import type { CompanyMembership } from '@/shared/types/auth.types'
import type {
  AcceptInvitationRequest,
  User,
  AuthTokens,
  LoginRequest,
  RegisterRequest,
} from '../types/auth.types'

type UILocale = 'en' | 'ru' | 'uz'
const isUILocale = (v: unknown): v is UILocale => v === 'en' || v === 'ru' || v === 'uz'

function syncPreferredLanguage(u: User | null): void {
  if (!u) return
  const stored = localStorage.getItem('hr_prescan_locale')
  if (isUILocale(u.language)) {
    if (stored !== u.language) setLocale(u.language)
  } else if (isUILocale(stored)) {
    saveUserLanguage(stored)
      .then(() => {
        u.language = stored
      })
      .catch((err: unknown) => console.warn('[auth] back-fill language failed', err))
  }
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const tokens = ref<AuthTokens | null>(loadTokens())
  const companies = ref<CompanyMembership[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!tokens.value?.access && !!user.value)
  const hasMultipleCompanies = computed(() => companies.value.length > 1)

  async function withLoading<T>(fn: () => Promise<T>): Promise<T> {
    loading.value = true
    error.value = null
    try {
      return await fn()
    } catch (err: unknown) {
      const msg = extractErrorMessage(err)
      error.value = msg
      throw new Error(msg)
    } finally {
      loading.value = false
    }
  }

  function setAuth(resp: { tokens: AuthTokens; user: User }): void {
    tokens.value = resp.tokens
    user.value = resp.user
    saveTokens(resp.tokens)
    syncPreferredLanguage(user.value)
  }

  async function login(data: LoginRequest): Promise<void> {
    await withLoading(async () => setAuth(await authService.login(data)))
  }
  async function googleLogin(credential: string): Promise<void> {
    await withLoading(async () => setAuth(await authService.googleAuth(credential)))
  }
  async function telegramLogin(data: { tokens: AuthTokens; user: User }): Promise<void> {
    setAuth(data)
  }
  async function register(data: RegisterRequest): Promise<void> {
    await withLoading(() => authService.register(data))
  }

  async function logout(): Promise<void> {
    try {
      if (tokens.value?.refresh) await authService.logout(tokens.value.refresh)
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
      syncPreferredLanguage(user.value)
    } catch {
      user.value = null
      tokens.value = null
      clearTokens()
    }
  }

  async function acceptInvitation(data: AcceptInvitationRequest): Promise<void> {
    await withLoading(() => authService.acceptInvitation(data))
  }

  async function acceptCompanyInvitation(token: string): Promise<void> {
    await withLoading(async () => {
      const resp = await authService.acceptCompanyInvitation(token)
      user.value = resp.user
    })
  }

  async function completeOnboarding(role: 'candidate' | 'hr'): Promise<void> {
    await withLoading(async () => setAuth(await authService.completeOnboarding(role)))
  }

  async function completeCompanySetup(
    data: Parameters<typeof authService.completeCompanySetup>[0],
  ): Promise<void> {
    await withLoading(async () => setAuth(await authService.completeCompanySetup(data)))
  }

  async function fetchCompanies(): Promise<void> {
    try {
      companies.value = await authService.getMyCompanies()
    } catch {
      companies.value = []
    }
  }

  async function switchCompany(companyId: string): Promise<void> {
    await withLoading(async () => {
      user.value = await authService.switchCompany(companyId)
    })
  }

  async function switchToPersonal(): Promise<void> {
    await withLoading(async () => {
      user.value = await authService.switchToPersonal()
    })
  }

  async function initAuth(): Promise<void> {
    const stored = loadTokens()
    if (!stored?.access) {
      tokens.value = null
      return
    }
    tokens.value = stored
    await fetchUser()
    if (user.value) await fetchCompanies()
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
    acceptCompanyInvitation,
    completeOnboarding,
    completeCompanySetup,
    fetchUser,
    fetchCompanies,
    switchCompany,
    switchToPersonal,
    initAuth,
  }
})
