import type { ApplicationStatus } from '@/shared/types/candidate.types'

export interface HiringFunnel {
  applied: number
  prescanned: number
  interviewed: number
  shortlisted: number
  hired: number
  rejected: number
  total: number
}

export interface VacancyPerformance {
  id: string
  title: string
  appCount: number
  interviewedCount: number
  hiredCount: number
  rejectedCount: number
  hireRate: number | string
  rejectionRate: number | string
  avgScore: number | string | null
}

export interface InterviewInsights {
  total: number
  completed: number
  completionRate: number
  averageScore: number | string | null
}

export interface StatusBreakdownItem {
  status: ApplicationStatus
  count: number
  percentage: number
}

export interface ScoreDistributionBucket {
  bucket: 'low' | 'medium' | 'good' | 'strong'
  count: number
}

export interface ProcessMetrics {
  activeVacancies: number
  pendingInterviews: number
  staleApplications: number
  averageDecisionDays: number | string | null
}

export interface CompanyAnalytics {
  funnel: HiringFunnel
  vacancyPerformance: VacancyPerformance[]
  interviewInsights: InterviewInsights
  statusBreakdown: StatusBreakdownItem[]
  scoreDistribution: ScoreDistributionBucket[]
  processMetrics: ProcessMetrics
}
