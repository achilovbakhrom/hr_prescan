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
