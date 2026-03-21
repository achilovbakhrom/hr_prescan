export type VacancyStatus = 'draft' | 'published' | 'paused' | 'archived'
export type VacancyVisibility = 'public' | 'private'
export type EmploymentType = 'full_time' | 'part_time' | 'contract' | 'internship'
export type ExperienceLevel = 'junior' | 'middle' | 'senior' | 'lead' | 'director'
export type QuestionSource = 'ai_generated' | 'hr_added'
export type InterviewMode = 'chat' | 'meet'
export type StepType = 'prescanning' | 'interview'

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
  companyInfo: string
  shareToken: string
  interviewDuration: number
  criteriaCount: number
  questionsCount: number
  createdAt: string
  updatedAt: string
}

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
