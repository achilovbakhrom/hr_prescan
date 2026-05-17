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
  hireRate: number
  rejectionRate: number
  avgScore: number | null
}

export interface InterviewInsights {
  total: number
  completed: number
  completionRate: number
  averageScore: number | null
}

export interface CompanyAnalytics {
  funnel: HiringFunnel
  vacancyPerformance: VacancyPerformance[]
  interviewInsights: InterviewInsights
}
