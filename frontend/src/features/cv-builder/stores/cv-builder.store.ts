import { ref } from 'vue'
import { defineStore } from 'pinia'
import { extractErrorMessage } from '@/shared/api/errors'
import { cvBuilderService } from '../services/cv-builder.service'
import type {
  CandidateProfile,
  CvGenerateResult,
  ProfileUpdatePayload,
  WorkExperiencePayload,
  EducationPayload,
  LanguagePayload,
  CertificationPayload,
} from '../types/cv-builder.types'

export const useCvBuilderStore = defineStore('cvBuilder', () => {
  const profile = ref<CandidateProfile | null>(null)
  const loading = ref(false)
  const saving = ref(false)
  const parsing = ref(false)
  const generating = ref(false)
  const improving = ref(false)
  const error = ref<string | null>(null)

  async function fetchProfile(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      profile.value = await cvBuilderService.getProfile()
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(data: ProfileUpdatePayload): Promise<void> {
    saving.value = true
    error.value = null
    try {
      await cvBuilderService.updateProfile(data)
      await fetchProfile()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      saving.value = false
    }
  }

  async function updateSkills(skills: string[]): Promise<void> {
    saving.value = true
    error.value = null
    try {
      await cvBuilderService.updateSkills(skills)
      await fetchProfile()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      saving.value = false
    }
  }

  // Work Experiences
  async function createWorkExperience(data: WorkExperiencePayload): Promise<void> {
    saving.value = true
    error.value = null
    try {
      await cvBuilderService.createWorkExperience(data)
      await fetchProfile()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      saving.value = false
    }
  }

  async function updateWorkExperience(id: string, data: WorkExperiencePayload): Promise<void> {
    saving.value = true
    error.value = null
    try {
      await cvBuilderService.updateWorkExperience(id, data)
      await fetchProfile()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      saving.value = false
    }
  }

  async function deleteWorkExperience(id: string): Promise<void> {
    saving.value = true
    error.value = null
    try {
      await cvBuilderService.deleteWorkExperience(id)
      await fetchProfile()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      saving.value = false
    }
  }

  // Educations
  async function createEducation(data: EducationPayload): Promise<void> {
    saving.value = true
    error.value = null
    try {
      await cvBuilderService.createEducation(data)
      await fetchProfile()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      saving.value = false
    }
  }

  async function updateEducation(id: string, data: EducationPayload): Promise<void> {
    saving.value = true
    error.value = null
    try {
      await cvBuilderService.updateEducation(id, data)
      await fetchProfile()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      saving.value = false
    }
  }

  async function deleteEducation(id: string): Promise<void> {
    saving.value = true
    error.value = null
    try {
      await cvBuilderService.deleteEducation(id)
      await fetchProfile()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      saving.value = false
    }
  }

  // Languages
  async function createLanguage(data: LanguagePayload): Promise<void> {
    saving.value = true
    error.value = null
    try {
      await cvBuilderService.createLanguage(data)
      await fetchProfile()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      saving.value = false
    }
  }

  async function updateLanguage(id: string, data: LanguagePayload): Promise<void> {
    saving.value = true
    error.value = null
    try {
      await cvBuilderService.updateLanguage(id, data)
      await fetchProfile()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      saving.value = false
    }
  }

  async function deleteLanguage(id: string): Promise<void> {
    saving.value = true
    error.value = null
    try {
      await cvBuilderService.deleteLanguage(id)
      await fetchProfile()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      saving.value = false
    }
  }

  // Certifications
  async function createCertification(data: CertificationPayload): Promise<void> {
    saving.value = true
    error.value = null
    try {
      await cvBuilderService.createCertification(data)
      await fetchProfile()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      saving.value = false
    }
  }

  async function updateCertification(id: string, data: CertificationPayload): Promise<void> {
    saving.value = true
    error.value = null
    try {
      await cvBuilderService.updateCertification(id, data)
      await fetchProfile()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      saving.value = false
    }
  }

  async function deleteCertification(id: string): Promise<void> {
    saving.value = true
    error.value = null
    try {
      await cvBuilderService.deleteCertification(id)
      await fetchProfile()
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      saving.value = false
    }
  }

  // CV PDF Generation
  async function generatePdf(
    template: string,
    name?: string,
  ): Promise<CvGenerateResult> {
    generating.value = true
    error.value = null
    try {
      const result = await cvBuilderService.generatePdf(template, name)
      await fetchProfile()
      return result
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      generating.value = false
    }
  }

  // CV Parsing (AI)
  async function parseCv(file: File): Promise<void> {
    parsing.value = true
    error.value = null
    try {
      profile.value = await cvBuilderService.parseCv(file)
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      parsing.value = false
    }
  }

  // CV Section Improvement (AI)
  async function improveCvSection(
    section: string,
    content: string,
    jobTitle?: string,
  ): Promise<string> {
    improving.value = true
    error.value = null
    try {
      const improved = await cvBuilderService.improveCvSection(section, content, jobTitle)
      return improved
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      improving.value = false
    }
  }

  return {
    profile,
    loading,
    saving,
    parsing,
    generating,
    improving,
    error,
    fetchProfile,
    updateProfile,
    updateSkills,
    createWorkExperience,
    updateWorkExperience,
    deleteWorkExperience,
    createEducation,
    updateEducation,
    deleteEducation,
    createLanguage,
    updateLanguage,
    deleteLanguage,
    createCertification,
    updateCertification,
    deleteCertification,
    generatePdf,
    parseCv,
    improveCvSection,
  }
})
