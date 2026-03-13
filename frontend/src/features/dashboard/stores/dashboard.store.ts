import { ref } from 'vue'
import { defineStore } from 'pinia'
import { dashboardService } from '../services/dashboard.service'
import type { DashboardStats } from '../types/dashboard.types'

export const useDashboardStore = defineStore('dashboard', () => {
  const stats = ref<DashboardStats | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchStats(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      stats.value = await dashboardService.getStats()
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  return {
    stats,
    loading,
    error,
    fetchStats,
  }
})

function extractErrorMessage(err: unknown): string {
  if (
    typeof err === 'object' &&
    err !== null &&
    'response' in err &&
    typeof (err as Record<string, unknown>).response === 'object'
  ) {
    const response = (err as { response: { data?: { message?: string } } })
      .response
    if (response.data?.message) {
      return response.data.message
    }
  }
  if (err instanceof Error) {
    return err.message
  }
  return 'An unexpected error occurred'
}
