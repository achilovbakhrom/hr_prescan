import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { extractErrorMessage } from '@/shared/api/errors'
import { setLocale, type SupportedLocale } from '@/shared/i18n'
import {
  LOCALE_STORAGE_KEY,
  isSupportedLocale,
  normalizeLocale,
} from '@/shared/i18n/supportedLocales'
import { saveUserLanguage } from '@/shared/services/language.service'
import { redirectToLogin } from '@/shared/api/authRedirect'
import { authService } from '../services/auth.service'
import { loadTokens, saveTokens, clearTokens } from './auth-tokens'
import { AUTH_TOKENS_CHANGED_EVENT } from '@/shared/api/authTokens'
import type {
  AccountMode,
  AccountModes,
  CompanyMembership,
  UserRole,
} from '@/shared/types/auth.types'
import type {
  AcceptInvitationRequest,
  User,
  AuthTokens,
  LoginRequest,
  RegisterRequest,
} from '../types/auth.types'

function syncPreferredLanguage(u: User | null): void {
  if (!u) return
  if (typeof localStorage === 'undefined') return
  const stored = normalizeLocale(localStorage.getItem(LOCALE_STORAGE_KEY))
  if (stored) {
    if (stored !== u.language) {
      saveUserLanguage(stored)
        .then(() => {
          u.language = stored
        })
        .catch((err: unknown) => console.warn('[auth] language sync failed', err))
    }
    setLocale(stored)
    return
  }

  if (isSupportedLocale(u.language)) {
    setLocale(u.language)
  } else {
    const fallback: SupportedLocale = 'en'
    setLocale(fallback)
    saveUserLanguage(fallback)
      .then(() => {
        u.language = fallback
      })
      .catch((err: unknown) => console.warn('[auth] language fallback failed', err))
  }
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const tokens = ref<AuthTokens | null>(loadTokens())
  const companies = ref<CompanyMembership[]>([])
  const modes = ref<AccountModes | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!tokens.value?.access && !!user.value)
  const hasMultipleCompanies = computed(() => companies.value.length > 1)
  const activeMode = computed<AccountMode>(() => {
    if (user.value?.activeMode) return user.value.activeMode
    return user.value?.role === 'candidate' ? 'candidate' : 'hr'
  })
  const currentAccessRole = computed<UserRole | null>(() => {
    if (!user.value) return null
    if (activeMode.value === 'candidate') return 'candidate'
    return user.value.role === 'candidate' ? 'candidate' : user.value.role
  })

  if (typeof window !== 'undefined') {
    window.addEventListener(AUTH_TOKENS_CHANGED_EVENT, () => {
      tokens.value = loadTokens()
    })
  }

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
      tokens.value = { ...tokens.value, ...response }
      saveTokens(tokens.value)
      return response.access
    } catch {
      user.value = null
      tokens.value = null
      clearTokens()
      redirectToLogin()
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

  async function fetchModes(): Promise<void> {
    if (!tokens.value?.access) return
    try {
      modes.value = await authService.getModes()
      user.value = modes.value.user
    } catch {
      modes.value = null
    }
  }

  function applyModes(result: AccountModes): void {
    modes.value = result
    user.value = result.user
  }

  async function switchMode(mode: AccountMode, companyId?: string): Promise<void> {
    await withLoading(async () => {
      applyModes(await authService.switchMode(mode, companyId))
      await fetchCompanies()
    })
  }

  async function createHrSpace(
    data: Parameters<typeof authService.createHrSpace>[0],
  ): Promise<void> {
    await withLoading(async () => {
      applyModes(await authService.createHrSpace(data))
      await fetchCompanies()
    })
  }

  async function createCandidateSpace(
    data: Parameters<typeof authService.createCandidateSpace>[0],
  ): Promise<void> {
    await withLoading(async () => {
      applyModes(await authService.createCandidateSpace(data))
      await fetchCompanies()
    })
  }

  async function switchCompany(companyId: string): Promise<void> {
    await withLoading(async () => {
      user.value = await authService.switchCompany(companyId)
      await fetchModes()
    })
  }

  async function switchToPersonal(): Promise<void> {
    await withLoading(async () => {
      user.value = await authService.switchToPersonal()
      await fetchModes()
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
    if (user.value) await fetchModes()
  }

  return {
    user,
    tokens,
    companies,
    modes,
    loading,
    error,
    isAuthenticated,
    hasMultipleCompanies,
    activeMode,
    currentAccessRole,
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
    fetchModes,
    switchCompany,
    switchToPersonal,
    switchMode,
    createHrSpace,
    createCandidateSpace,
    initAuth,
  }
})
