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

export interface CompanyAnalytics {
  funnel: HiringFunnel
  vacancyPerformance: VacancyPerformance[]
  interviewInsights: InterviewInsights
}
