import { ref } from 'vue'
import { defineStore } from 'pinia'
import { adminService } from '../services/admin.service'
import type { AdminCompany, AdminUser, PlatformAnalytics } from '../types/admin.types'
import type { SubscriptionPlan } from '@/shared/types/subscription.types'

export const useAdminStore = defineStore('admin', () => {
  const companies = ref<AdminCompany[]>([])
  const companiesCount = ref(0)
  const users = ref<AdminUser[]>([])
  const usersCount = ref(0)
  const analytics = ref<PlatformAnalytics | null>(null)
  const plans = ref<SubscriptionPlan[]>([])
  const loading = ref(false)
  // Per-row mutation spinner — so toggling one row doesn't freeze the whole table.
  const mutatingIds = ref<Set<string>>(new Set())
  const error = ref<string | null>(null)

  function isMutating(id: string): boolean {
    return mutatingIds.value.has(id)
  }

  async function withRowMutation<T>(id: string, fn: () => Promise<T>): Promise<T> {
    // new Set() so Vue reactivity picks up the change (Sets are mutable refs).
    mutatingIds.value = new Set(mutatingIds.value).add(id)
    try {
      return await fn()
    } finally {
      const next = new Set(mutatingIds.value)
      next.delete(id)
      mutatingIds.value = next
    }
  }

  async function fetchCompanies(params?: { search?: string; page?: number }): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const response = await adminService.getCompanies(params)
      companies.value = response.results
      companiesCount.value = response.count
    } catch {
      error.value = 'Failed to load companies'
    } finally {
      loading.value = false
    }
  }

  async function toggleCompanyStatus(id: string, isActive: boolean): Promise<void> {
    await withRowMutation(id, async () => {
      try {
        const updated = await adminService.toggleCompanyStatus(id, isActive)
        const index = companies.value.findIndex((c) => c.id === id)
        if (index !== -1) {
          companies.value[index] = updated
        }
      } catch {
        error.value = 'Failed to update company status'
      }
    })
  }

  async function fetchUsers(params?: {
    search?: string
    role?: string
    page?: number
  }): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const response = await adminService.getUsers(params)
      users.value = response.results
      usersCount.value = response.count
    } catch {
      error.value = 'Failed to load users'
    } finally {
      loading.value = false
    }
  }

  async function toggleUserStatus(id: string, isActive: boolean): Promise<void> {
    await withRowMutation(id, async () => {
      try {
        const updated = await adminService.toggleUserStatus(id, isActive)
        const index = users.value.findIndex((u) => u.id === id)
        if (index !== -1) {
          users.value[index] = updated
        }
      } catch {
        error.value = 'Failed to update user status'
      }
    })
  }

  async function fetchAnalytics(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      analytics.value = await adminService.getAnalytics()
    } catch {
      error.value = 'Failed to load analytics'
    } finally {
      loading.value = false
    }
  }

  async function fetchPlans(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      plans.value = await adminService.getPlans()
    } catch {
      error.value = 'Failed to load plans'
    } finally {
      loading.value = false
    }
  }

  async function updatePlan(id: string, data: Partial<SubscriptionPlan>): Promise<void> {
    await withRowMutation(id, async () => {
      try {
        const updated = await adminService.updatePlan(id, data)
        const index = plans.value.findIndex((p) => p.id === id)
        if (index !== -1) {
          plans.value[index] = updated
        }
      } catch {
        error.value = 'Failed to update plan'
      }
    })
  }

  return {
    companies,
    companiesCount,
    users,
    usersCount,
    analytics,
    plans,
    loading,
    mutatingIds,
    isMutating,
    error,
    fetchCompanies,
    toggleCompanyStatus,
    fetchUsers,
    toggleUserStatus,
    fetchAnalytics,
    fetchPlans,
    updatePlan,
  }
})
