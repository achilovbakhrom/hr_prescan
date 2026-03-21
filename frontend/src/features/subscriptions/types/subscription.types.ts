// Re-export shared types so intra-feature imports still work
export type { SubscriptionPlan, PlanTier } from '@/shared/types/subscription.types'

// Import shared types needed by feature-specific interfaces
import type { SubscriptionPlan } from '@/shared/types/subscription.types'

export type BillingPeriod = 'monthly' | 'yearly'

export interface CompanySubscription {
  id: string
  plan: SubscriptionPlan
  billingPeriod: BillingPeriod
  currentPeriodStart: string
  currentPeriodEnd: string
  isActive: boolean
}

export interface SubscriptionUsage {
  vacancies: { used: number; limit: number }
  interviews: { used: number; limit: number }
  hrUsers: { used: number; limit: number }
  storage: { usedGb: number; limitGb: number }
}
