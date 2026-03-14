export interface AdminCompany {
  id: string
  name: string
  industry: string
  size: string
  country: string
  subscriptionStatus: string
  planTier: string
  usersCount: number
  vacanciesCount: number
  isActive: boolean
  createdAt: string
}

export interface AdminUser {
  id: string
  email: string
  firstName: string
  lastName: string
  role: string
  companyName: string | null
  isActive: boolean
  createdAt: string
}

export interface PlatformAnalytics {
  totalCompanies: number
  totalUsers: number
  totalInterviews: number
  activeSubscriptions: number
  monthlyRevenue: number
}
