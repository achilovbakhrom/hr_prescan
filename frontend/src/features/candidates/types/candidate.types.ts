export type ApplicationStatus =
  | 'applied'
  | 'interview_in_progress'
  | 'interview_completed'
  | 'reviewing'
  | 'shortlisted'
  | 'rejected'
  | 'expired'

export interface Application {
  id: string
  vacancyId: string
  vacancyTitle: string
  candidateName: string
  candidateEmail: string
  candidatePhone: string
  cvFile: string
  cvOriginalFilename: string
  matchScore: number | null
  interviewScore: number | null
  status: ApplicationStatus
  createdAt: string
  updatedAt: string
}

export interface ApplicationDetail extends Application {
  cvParsedText: string
  cvParsedData: CvParsedData
  matchDetails: Record<string, number>
  hrNotes: string
  interviewToken?: string
  screeningMode?: 'chat' | 'meet'
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
}
