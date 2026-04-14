import { ref } from 'vue'
import { defineStore } from 'pinia'
import { subscriptionService } from '../services/subscription.service'
import type {
  SubscriptionPlan,
  CompanySubscription,
  BillingPeriod,
  SubscriptionUsage,
} from '../types/subscription.types'

export const useSubscriptionStore = defineStore('subscription', () => {
  const plans = ref<SubscriptionPlan[]>([])
  const currentSubscription = ref<CompanySubscription | null>(null)
  const usage = ref<SubscriptionUsage | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchPlans(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      plans.value = await subscriptionService.getPlans()
    } catch {
      error.value = 'Failed to load subscription plans'
    } finally {
      loading.value = false
    }
  }

  async function fetchCurrentSubscription(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentSubscription.value = await subscriptionService.getCurrentSubscription()
    } catch {
      error.value = 'Failed to load current subscription'
    } finally {
      loading.value = false
    }
  }

  async function subscribe(planId: string, billingPeriod: BillingPeriod): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentSubscription.value = await subscriptionService.subscribe(planId, billingPeriod)
    } catch {
      error.value = 'Failed to subscribe to plan'
      throw new Error(error.value)
    } finally {
      loading.value = false
    }
  }

  async function cancelSubscription(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      await subscriptionService.cancelSubscription()
      if (currentSubscription.value) {
        currentSubscription.value.isActive = false
      }
    } catch {
      error.value = 'Failed to cancel subscription'
      throw new Error(error.value)
    } finally {
      loading.value = false
    }
  }

  async function fetchUsage(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      usage.value = await subscriptionService.getUsage()
    } catch {
      error.value = 'Failed to load usage data'
    } finally {
      loading.value = false
    }
  }

  return {
    plans,
    currentSubscription,
    usage,
    loading,
    error,
    fetchPlans,
    fetchCurrentSubscription,
    subscribe,
    cancelSubscription,
    fetchUsage,
  }
})
