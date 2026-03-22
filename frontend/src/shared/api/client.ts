import axios, {
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'

const TOKENS_KEY = 'hr_prescan_tokens'

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

/**
 * Convert camelCase keys to snake_case (Django convention).
 */
function toSnakeCase(str: string): string {
  return str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`)
}

function convertKeysToSnakeCase(obj: unknown): unknown {
  if (Array.isArray(obj)) {
    return obj.map(convertKeysToSnakeCase)
  }
  if (obj !== null && typeof obj === 'object' && !(obj instanceof File) && !(obj instanceof Blob) && !(obj instanceof FormData)) {
    return Object.fromEntries(
      Object.entries(obj as Record<string, unknown>).map(([key, value]) => [
        toSnakeCase(key),
        convertKeysToSnakeCase(value),
      ]),
    )
  }
  return obj
}

/**
 * Convert snake_case keys to camelCase (frontend convention).
 */
function toCamelCase(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter: string) => letter.toUpperCase())
}

function convertKeysToCamelCase(obj: unknown): unknown {
  if (Array.isArray(obj)) {
    return obj.map(convertKeysToCamelCase)
  }
  if (obj !== null && typeof obj === 'object') {
    return Object.fromEntries(
      Object.entries(obj as Record<string, unknown>).map(([key, value]) => [
        toCamelCase(key),
        convertKeysToCamelCase(value),
      ]),
    )
  }
  return obj
}

const baseURL = (import.meta.env.VITE_API_URL as string).replace(/\/$/, '')

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
})

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

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add locale header for server-side i18n
    const locale = localStorage.getItem('hr_prescan_locale') || 'en'
    config.headers['Accept-Language'] = locale

    const raw = localStorage.getItem(TOKENS_KEY)
    if (raw) {
      try {
        const tokens = JSON.parse(raw) as { access: string }
        config.headers.Authorization = `Bearer ${tokens.access}`
      } catch {
        // Invalid token data, skip
      }
    }
    return config
  },
)

let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (error: unknown) => void
}> = []

function processQueue(error: unknown, token: string | null): void {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error)
    } else if (token) {
      promise.resolve(token)
    }
  })
  failedQueue = []
}

function redirectToLogin(): void {
  if (window.location.pathname !== '/login') {
    window.location.href = '/login'
  }
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

    if (
      axiosError.response?.status !== 401 ||
      originalRequest._retry ||
      isAuthEndpoint
    ) {
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`
        return apiClient(originalRequest)
      })
    }

    originalRequest._retry = true
    isRefreshing = true

    const raw = localStorage.getItem(TOKENS_KEY)
    if (!raw) {
      isRefreshing = false
      redirectToLogin()
      return Promise.reject(error)
    }

    try {
      const tokens = JSON.parse(raw) as { access: string; refresh: string }
      const response = await axios.post<{ access: string }>(
        `${import.meta.env.VITE_API_URL}/auth/token/refresh/`,
        { refresh: tokens.refresh },
      )

      const newAccess = response.data.access
      const updatedTokens = { ...tokens, access: newAccess }
      localStorage.setItem(TOKENS_KEY, JSON.stringify(updatedTokens))

      processQueue(null, newAccess)
      originalRequest.headers.Authorization = `Bearer ${newAccess}`
      return apiClient(originalRequest)
    } catch (refreshError) {
      processQueue(refreshError, null)
      localStorage.removeItem(TOKENS_KEY)
      redirectToLogin()
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  },
)
