export type PlanTier = 'free' | 'starter' | 'professional' | 'enterprise'

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
