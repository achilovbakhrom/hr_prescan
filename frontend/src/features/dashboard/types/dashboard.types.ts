export interface DashboardStats {
  activeVacanciesCount: number
  totalCandidatesCount: number
  pendingInterviewsCount: number
  completedInterviewsCount: number
  averageMatchScore: number | null
  recentApplications: RecentApplication[]
  upcomingInterviews: UpcomingInterview[]
}

export interface RecentApplication {
  id: string
  candidateName: string
  vacancyTitle: string
  matchScore: number | null
  status: string
  createdAt: string
}

export interface UpcomingInterview {
  id: string
  candidateName: string
  vacancyTitle: string
  createdAt: string
  status: string
}
