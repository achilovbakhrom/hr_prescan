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
      await apiClient.get<CompanySubscription>('/hr/subscription')
    return response.data
  },

  async subscribe(
    planTier: string,
    billingPeriod: BillingPeriod,
  ): Promise<CompanySubscription> {
    const response = await apiClient.post<CompanySubscription>(
      '/hr/subscription',
      { planTier, billingPeriod },
    )
    return response.data
  },

  async cancelSubscription(): Promise<void> {
    await apiClient.post('/hr/subscription/cancel')
  },

  async getUsage(): Promise<SubscriptionUsage> {
    const response =
      await apiClient.get<SubscriptionUsage>('/hr/subscription/usage')
    return response.data
  },
}
