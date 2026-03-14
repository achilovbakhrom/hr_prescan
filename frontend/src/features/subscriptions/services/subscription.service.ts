import { apiClient } from '@/shared/api/client'
import type {
  SubscriptionPlan,
  CompanySubscription,
  BillingPeriod,
  SubscriptionUsage,
} from '../types/subscription.types'

export const subscriptionService = {
  async getPlans(): Promise<SubscriptionPlan[]> {
    const response =
      await apiClient.get<SubscriptionPlan[]>('/subscriptions/plans')
    return response.data
  },

  async getCurrentSubscription(): Promise<CompanySubscription> {
    const response =
      await apiClient.get<CompanySubscription>('/subscriptions/current')
    return response.data
  },

  async subscribe(
    planId: string,
    billingPeriod: BillingPeriod,
  ): Promise<CompanySubscription> {
    const response = await apiClient.post<CompanySubscription>(
      '/subscriptions/subscribe',
      { planId, billingPeriod },
    )
    return response.data
  },

  async cancelSubscription(): Promise<void> {
    await apiClient.post('/subscriptions/cancel')
  },

  async getUsage(): Promise<SubscriptionUsage> {
    const response =
      await apiClient.get<SubscriptionUsage>('/subscriptions/usage')
    return response.data
  },
}
