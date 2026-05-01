export type VacancyStatus = 'draft' | 'published' | 'paused' | 'archived'
export type VacancyVisibility = 'public' | 'private'
export type EmploymentType = 'full_time' | 'part_time' | 'contract' | 'internship'
export type ExperienceLevel = 'junior' | 'middle' | 'senior' | 'lead' | 'director'
export type InterviewMode = 'chat' | 'meet'

export interface Vacancy {
  id: string
  title: string
  description: string
  requirements: string
  responsibilities: string
  skills: string[]
  salaryMin: number | null
  salaryMax: number | null
  salaryCurrency: string
  location: string
  isRemote: boolean
  employmentType: EmploymentType
  experienceLevel: ExperienceLevel
  deadline: string | null
  status: VacancyStatus
  visibility: VacancyVisibility
  interviewMode: InterviewMode
  interviewEnabled: boolean
  cvRequired: boolean
  prescanningLanguage: string
  companyInfo: string
  shareToken: string
  interviewDuration: number
  criteriaCount: number
  questionsCount: number
  candidatesTotal: number
  candidatesInterviewed: number
  candidatesShortlisted: number
  candidatesRejected: number
  candidatesHired: number
  keywords: string[]
  telegramCode: number | null
  titleTranslations?: Record<string, string>
  descriptionTranslations?: Record<string, string>
  requirementsTranslations?: Record<string, string>
  responsibilitiesTranslations?: Record<string, string>
  createdByEmail: string
  createdAt: string
  updatedAt: string
  /** Company id returned alongside vacancy lists */
  companyId?: string | null
  /** Company name returned by some API endpoints */
  companyName?: string | null
  /** Company logo URL returned by list endpoints (may be absent on detail) */
  companyLogo?: string | null
  canApply?: boolean
  contentSource?: 'internal' | 'parsed'
  externalUrl?: string
}
