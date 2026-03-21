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
  companyInfo: string
  shareToken: string
  interviewDuration: number
  criteriaCount: number
  questionsCount: number
  createdAt: string
  updatedAt: string
}
