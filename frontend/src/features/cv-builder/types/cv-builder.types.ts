export interface SkillItem {
  slug: string
  name: string
  category: string
}

export interface WorkExperience {
  id: string
  companyName: string
  position: string
  employmentType: string
  location: string
  startDate: string
  endDate: string | null
  isCurrent: boolean
  description: string
  order: number
}

export interface EducationLevelRef {
  slug: string
  name: string
}

export interface Education {
  id: string
  institution: string
  degree: string
  educationLevel: EducationLevelRef | null
  fieldOfStudy: string
  startDate: string
  endDate: string | null
  description: string
  order: number
}

export interface LanguageRef {
  code: string
  name: string
}

export interface LanguageEntry {
  id: string
  language: LanguageRef
  proficiency: string
}

export interface Certification {
  id: string
  name: string
  issuingOrganization: string
  issueDate: string | null
  expiryDate: string | null
  credentialUrl: string
  image: string | null
  order: number
}

export interface CvFile {
  id: string
  name: string
  template: string
  file: string
  isActive: boolean
  createdAt: string
}

export interface CompletenessSection {
  personal: boolean
  summary: boolean
  experience: boolean
  education: boolean
  skills: boolean
  languages: boolean
}

export interface Completeness {
  score: number
  sections: CompletenessSection
}

export interface CandidateProfile {
  id: string
  headline: string
  summary: string
  location: string
  dateOfBirth: string | null
  linkedinUrl: string
  githubUrl: string
  websiteUrl: string
  desiredSalaryMin: number | null
  desiredSalaryMax: number | null
  desiredSalaryCurrency: string
  desiredEmploymentType: string
  isOpenToWork: boolean
  photo: string | null
  skills: SkillItem[]
  workExperiences: WorkExperience[]
  educations: Education[]
  languages: LanguageEntry[]
  certifications: Certification[]
  cvs: CvFile[]
  completeness: Completeness
}

export interface ProfileUpdatePayload {
  headline?: string
  summary?: string
  location?: string
  dateOfBirth?: string | null
  linkedinUrl?: string
  githubUrl?: string
  websiteUrl?: string
  desiredSalaryMin?: number | null
  desiredSalaryMax?: number | null
  desiredSalaryCurrency?: string
  desiredEmploymentType?: string
  isOpenToWork?: boolean
}

export interface WorkExperiencePayload {
  companyName: string
  position: string
  employmentType: string
  location: string
  startDate: string
  endDate: string | null
  isCurrent: boolean
  description: string
}

export interface EducationPayload {
  institution: string
  degree: string
  educationLevel: string
  fieldOfStudy: string
  startDate: string
  endDate: string | null
  description: string
}

export interface LanguagePayload {
  language: string
  proficiency: string
}

export interface CertificationPayload {
  name: string
  issuingOrganization: string
  issueDate: string | null
  expiryDate: string | null
  credentialUrl: string
}

export interface CvGenerateResult {
  id: string
  name: string
  template: string
  file: string
  isActive: boolean
  downloadUrl: string
}
