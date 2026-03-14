export type PlanTier = 'free' | 'starter' | 'professional' | 'enterprise'
export type BillingPeriod = 'monthly' | 'yearly'

export interface SubscriptionPlan {
  id: string
  name: string
  tier: PlanTier
  description: string
  priceMonthly: number
  priceYearly: number
  maxVacancies: number
  maxInterviewsPerMonth: number
  maxHrUsers: number
  maxStorageGb: number
}

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
