import { apiClient } from '@/shared/api/client'
import type {
  CandidateProfile,
  WorkExperience,
  WorkExperiencePayload,
  Education,
  EducationPayload,
  LanguageEntry,
  LanguagePayload,
  Certification,
  CertificationPayload,
  ProfileUpdatePayload,
  Completeness,
  CvGenerateResult,
  CvChatMessage,
  CvChatResponse,
} from '../types/cv-builder.types'

const BASE = '/candidate/profile'

export const cvBuilderService = {
  async getProfile(): Promise<CandidateProfile> {
    const response = await apiClient.get<CandidateProfile>(BASE)
    return response.data
  },

  async updateProfile(data: ProfileUpdatePayload): Promise<CandidateProfile> {
    const response = await apiClient.patch<CandidateProfile>(BASE, data)
    return response.data
  },

  async updateSkills(skills: string[]): Promise<void> {
    await apiClient.put(`${BASE}/skills`, { skills })
  },

  async getCompleteness(): Promise<Completeness> {
    const response = await apiClient.get<Completeness>(`${BASE}/completeness`)
    return response.data
  },

  // Work Experiences
  async createWorkExperience(data: WorkExperiencePayload): Promise<WorkExperience> {
    const response = await apiClient.post<WorkExperience>(`${BASE}/work-experiences`, data)
    return response.data
  },

  async updateWorkExperience(id: string, data: WorkExperiencePayload): Promise<WorkExperience> {
    const response = await apiClient.patch<WorkExperience>(`${BASE}/work-experiences/${id}`, data)
    return response.data
  },

  async deleteWorkExperience(id: string): Promise<void> {
    await apiClient.delete(`${BASE}/work-experiences/${id}`)
  },

  // Educations
  async createEducation(data: EducationPayload): Promise<Education> {
    const response = await apiClient.post<Education>(`${BASE}/educations`, data)
    return response.data
  },

  async updateEducation(id: string, data: EducationPayload): Promise<Education> {
    const response = await apiClient.patch<Education>(`${BASE}/educations/${id}`, data)
    return response.data
  },

  async deleteEducation(id: string): Promise<void> {
    await apiClient.delete(`${BASE}/educations/${id}`)
  },

  // Languages
  async createLanguage(data: LanguagePayload): Promise<LanguageEntry> {
    const response = await apiClient.post<LanguageEntry>(`${BASE}/languages`, data)
    return response.data
  },

  async updateLanguage(id: string, data: LanguagePayload): Promise<LanguageEntry> {
    const response = await apiClient.patch<LanguageEntry>(`${BASE}/languages/${id}`, data)
    return response.data
  },

  async deleteLanguage(id: string): Promise<void> {
    await apiClient.delete(`${BASE}/languages/${id}`)
  },

  // Certifications
  async createCertification(data: CertificationPayload): Promise<Certification> {
    const response = await apiClient.post<Certification>(`${BASE}/certifications`, data)
    return response.data
  },

  async updateCertification(id: string, data: CertificationPayload): Promise<Certification> {
    const response = await apiClient.patch<Certification>(`${BASE}/certifications/${id}`, data)
    return response.data
  },

  async deleteCertification(id: string): Promise<void> {
    await apiClient.delete(`${BASE}/certifications/${id}`)
  },

  // CV PDF Generation
  async generatePdf(template: string, name?: string): Promise<CvGenerateResult> {
    const { data } = await apiClient.post<CvGenerateResult>(`${BASE}/cv/generate-pdf`, {
      template,
      name,
    })
    return data
  },

  // CV Parsing (AI)
  async parseCv(file: File): Promise<CandidateProfile> {
    const formData = new FormData()
    formData.append('cv_file', file)
    const { data } = await apiClient.post<CandidateProfile>(`${BASE}/cv/parse`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  // CV AI Chat — conversational CV generation
  async cvAiChat(messages: CvChatMessage[]): Promise<CvChatResponse> {
    const { data } = await apiClient.post<CvChatResponse>(`${BASE}/cv/ai-chat`, { messages })
    return data
  },

  async cvAiGenerate(messages: CvChatMessage[]): Promise<CandidateProfile> {
    const { data: profile } = await apiClient.post<CandidateProfile>(`${BASE}/cv/ai-generate`, { messages })
    return profile
  },

  // CV Section Improvement (AI)
  async improveCvSection(
    section: string,
    content: string,
    jobTitle?: string,
  ): Promise<string> {
    const { data } = await apiClient.post<{ improved: string }>(`${BASE}/cv/improve-section`, {
      section,
      content,
      jobTitle,
    })
    return data.improved
  },
}
