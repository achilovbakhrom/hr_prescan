// Re-export shared types so intra-feature imports still work
export type { Application, ApplicationStatus } from '@/shared/types/candidate.types'

// Import shared types needed by feature-specific interfaces
import type { Application } from '@/shared/types/candidate.types'

export interface ApplicationDetail extends Application {
  cvParsedText: string
  cvParsedData: CvParsedData
  matchDetails: Record<string, unknown>
  matchNotesTranslations: Record<string, string>
  cvSummaryTranslations: Record<string, string>
  hrNotes: string
  prescanToken?: string
  interviewToken?: string
  interviewEnabled?: boolean
  interviewMode?: string
  companyName?: string
  hiringManagerToken?: string
  hiringManagerFeedback?: HiringManagerFeedback[]
  events?: ApplicationEvent[]
}

export interface HiringManagerFeedback {
  id: string
  reviewerName: string
  reviewerRole: string
  recommendation: 'advance' | 'maybe' | 'reject'
  rating: number | null
  comment: string
  createdAt: string
}

export interface ApplicationEvent {
  id: string
  eventType: 'share_link_rotated' | 'hiring_manager_feedback'
  actorName: string
  message: string
  metadata: Record<string, unknown>
  createdAt: string
}

export interface CvParsedData {
  skills: string[]
  experience: ExperienceEntry[]
  education: EducationEntry[]
}

export interface ExperienceEntry {
  company: string
  position: string
  duration: string
  description: string
}

export interface EducationEntry {
  institution: string
  degree: string
  field: string
  year: string
}

export interface SubmitApplicationRequest {
  candidateName: string
  candidateEmail: string
  candidatePhone?: string
  cvFile?: File
  cvId?: string
}

export interface HRCandidateRecord {
  id: string
  candidateName: string
  candidateEmail: string
  candidatePhone: string
  applicationCount: number
  latestApplicationId: string | null
  latestVacancyId: string | null
  latestVacancyTitle: string
  latestCompanyName: string
  latestStatus: Application['status'] | ''
  latestMatchScore: number | string | null
  latestPrescanningScore: number | null
  latestInterviewScore: number | null
  firstSeenAt: string
  lastActivityAt: string
  createdAt: string
  updatedAt: string
}

export interface HRCandidateRecordDetail extends HRCandidateRecord {
  notes: string
  applications: Application[]
}

export interface HRCandidateRecordUpdate {
  candidateName?: string
  candidatePhone?: string
  notes?: string
}
