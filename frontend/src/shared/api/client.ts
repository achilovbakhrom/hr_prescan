import axios, { AxiosHeaders, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'
import { clearTokens, loadTokens, saveTokens, type StoredAuthTokens } from './authTokens'
import { convertKeysToCamelCase, convertKeysToSnakeCase } from './caseTransform'

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

const baseURL = ((import.meta.env.VITE_API_URL as string | undefined) ?? '/api').replace(/\/$/, '')

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
})

const refreshClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
})

interface RefreshResponse {
  access: string
  refresh?: string
}

function setAuthorizationHeader(config: InternalAxiosRequestConfig, token: string): void {
  const headers = AxiosHeaders.from(config.headers)
  headers.set('Authorization', `Bearer ${token}`)
  config.headers = headers
}

// Ensure trailing slash + convert request body & params keys to snake_case
apiClient.interceptors.request.use((config) => {
  if (config.url && !config.url.endsWith('/')) {
    config.url += '/'
  }
  if (config.data && typeof config.data === 'object') {
    config.data = convertKeysToSnakeCase(config.data)
  }
  if (config.params && typeof config.params === 'object') {
    config.params = convertKeysToSnakeCase(config.params)
  }
  return config
})

// Convert response body keys to camelCase (skip binary responses)
apiClient.interceptors.response.use((response) => {
  if (
    response.data &&
    typeof response.data === 'object' &&
    !(response.data instanceof Blob) &&
    !(response.data instanceof ArrayBuffer)
  ) {
    response.data = convertKeysToCamelCase(response.data)
  }
  return response
})

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // Add locale header for server-side i18n
  const locale = localStorage.getItem('hr_prescan_locale') || 'en'
  config.headers['Accept-Language'] = locale

  const tokens = loadTokens()
  if (tokens?.access) setAuthorizationHeader(config, tokens.access)
  return config
})

let refreshPromise: Promise<StoredAuthTokens> | null = null

function redirectToLogin(): void {
  if (window.location.pathname !== '/login') {
    window.location.href = '/login'
  }
}

async function refreshStoredTokens(): Promise<StoredAuthTokens> {
  const tokens = loadTokens()
  if (!tokens?.refresh) throw new Error('Missing refresh token')

  const response = await refreshClient.post<RefreshResponse>('/auth/token/refresh/', {
    refresh: tokens.refresh,
  })
  const updatedTokens = {
    access: response.data.access,
    refresh: response.data.refresh ?? tokens.refresh,
  }
  saveTokens(updatedTokens)
  return updatedTokens
}

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: unknown) => {
    const axiosError = error as {
      config?: RetryableRequestConfig
      response?: { status: number }
    }

    const originalRequest = axiosError.config
    if (!originalRequest) {
      return Promise.reject(error)
    }

    const isAuthEndpoint =
      originalRequest.url?.includes('/auth/login') ||
      originalRequest.url?.includes('/auth/token/refresh')

    if (axiosError.response?.status !== 401 || originalRequest._retry || isAuthEndpoint) {
      return Promise.reject(error)
    }

    originalRequest._retry = true
    refreshPromise ??= refreshStoredTokens().finally(() => {
      refreshPromise = null
    })

    try {
      const tokens = await refreshPromise
      setAuthorizationHeader(originalRequest, tokens.access)
      return apiClient(originalRequest)
    } catch (refreshError) {
      clearTokens()
      redirectToLogin()
      return Promise.reject(refreshError)
    }
  },
)
