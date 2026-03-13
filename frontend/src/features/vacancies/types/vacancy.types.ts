export type VacancyStatus = 'draft' | 'published' | 'paused' | 'closed'
export type VacancyVisibility = 'public' | 'private'
export type EmploymentType = 'full_time' | 'part_time' | 'contract' | 'internship'
export type ExperienceLevel = 'junior' | 'middle' | 'senior' | 'lead' | 'director'
export type QuestionSource = 'ai_generated' | 'hr_added'

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
  shareToken: string
  interviewDuration: number
  criteriaCount: number
  questionsCount: number
  createdAt: string
  updatedAt: string
}

export interface VacancyDetail extends Vacancy {
  criteria: VacancyCriteria[]
  questions: InterviewQuestion[]
}

export interface VacancyCriteria {
  id: string
  name: string
  description: string
  weight: number
  isDefault: boolean
  order: number
}

export interface InterviewQuestion {
  id: string
  text: string
  category: string
  source: QuestionSource
  order: number
  isActive: boolean
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
  interviewDuration?: number
}

export interface UpdateVacancyRequest extends Partial<CreateVacancyRequest> {}
