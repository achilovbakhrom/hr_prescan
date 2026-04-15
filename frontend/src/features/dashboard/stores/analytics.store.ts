import { ref } from 'vue'
import { defineStore } from 'pinia'
import { extractErrorMessage } from '@/shared/api/errors'
import { analyticsService } from '../services/analytics.service'
import type { CompanyAnalytics } from '../types/analytics.types'

export const useAnalyticsStore = defineStore('analytics', () => {
  const analytics = ref<CompanyAnalytics | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAnalytics(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      analytics.value = await analyticsService.getCompanyAnalytics()
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  return {
    analytics,
    loading,
    error,
    fetchAnalytics,
  }
})
