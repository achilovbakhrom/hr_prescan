// Re-export shared types so intra-feature imports still work
export type {
  Vacancy,
  VacancyStatus,
  VacancyVisibility,
  EmploymentType,
  ExperienceLevel,
  InterviewMode,
} from '@/shared/types/vacancy.types'

// Import shared types needed by feature-specific interfaces
import type { Vacancy, EmploymentType, ExperienceLevel, VacancyVisibility, InterviewMode } from '@/shared/types/vacancy.types'

export type QuestionSource = 'ai_generated' | 'hr_added'
export type StepType = 'prescanning' | 'interview'

export interface VacancyDetail extends Vacancy {
  prescanningPrompt: string
  interviewPrompt: string
  criteria: VacancyCriteria[]
  questions: InterviewQuestion[]
  createdByEmail: string
}

export interface VacancyCriteria {
  id: string
  name: string
  description: string
  weight: number
  isDefault: boolean
  order: number
  step: StepType
}

export interface InterviewQuestion {
  id: string
  text: string
  category: string
  source: QuestionSource
  order: number
  isActive: boolean
  step: StepType
}

export interface CreateVacancyRequest {
  title: string
  description: string
  requirements?: string
  responsibilities?: string
  skills?: string[]
  salaryMin?: number | null
  salaryMax?: number | null
  salaryCurrency?: string
  location?: string
  isRemote?: boolean
  employmentType?: EmploymentType
  experienceLevel?: ExperienceLevel
  deadline?: string | null
  visibility?: VacancyVisibility
  interviewMode?: InterviewMode
  interviewEnabled?: boolean
  cvRequired?: boolean
  interviewDuration?: number
  companyInfo?: string
  prescanningPrompt?: string
  interviewPrompt?: string
}

export interface UpdateVacancyRequest extends Partial<CreateVacancyRequest> {}
