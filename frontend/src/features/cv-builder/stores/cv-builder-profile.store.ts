import { ref } from 'vue'
import { defineStore } from 'pinia'
import { extractApiError, type FieldErrors } from '@/shared/api/errors'
import { cvBuilderService } from '../services/cv-builder.service'
import type {
  CandidateProfile,
  ProfileUpdatePayload,
  WorkExperiencePayload,
  EducationPayload,
  LanguagePayload,
  CertificationPayload,
} from '../types/cv-builder.types'

const EMPTY_PROFILE: CandidateProfile = {
  id: '',
  headline: '',
  summary: '',
  location: '',
  dateOfBirth: null,
  linkedinUrl: '',
  githubUrl: '',
  websiteUrl: '',
  desiredSalaryMin: null,
  desiredSalaryMax: null,
  desiredSalaryCurrency: 'USD',
  desiredSalaryNegotiable: false,
  desiredEmploymentType: '',
  isOpenToWork: false,
  shareToken: '',
  photo: null,
  photoUrl: null,
  skills: [],
  workExperiences: [],
  educations: [],
  languages: [],
  certifications: [],
  cvs: [],
  completeness: {
    score: 0,
    sections: {
      personal: false,
      summary: false,
      experience: false,
      education: false,
      skills: false,
      languages: false,
    },
  },
}

export const useCvBuilderProfileStore = defineStore('cvBuilderProfile', () => {
  const profile = ref<CandidateProfile | null>(null)
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<string | null>(null)
  const fieldErrors = ref<FieldErrors>({})

  function clearErrors(): void {
    error.value = null
    fieldErrors.value = {}
  }

  function handleError(err: unknown): never {
    const apiError = extractApiError(err)
    error.value = apiError.message
    if ('fieldErrors' in apiError) {
      fieldErrors.value = (apiError as { fieldErrors: FieldErrors }).fieldErrors
    }
    throw apiError
  }

  /** DRY wrapper: set saving, clear errors, run action, refresh profile. */
  async function withSave<T>(action: () => Promise<T>): Promise<T> {
    saving.value = true
    clearErrors()
    try {
      const result = await action()
      await fetchProfile()
      return result
    } catch (err: unknown) {
      saving.value = false
      handleError(err)
    } finally {
      saving.value = false
    }
  }

  async function fetchProfile(): Promise<void> {
    loading.value = true
    clearErrors()
    try {
      const result = await cvBuilderService.getProfile()
      profile.value = result || { ...EMPTY_PROFILE }
    } catch (err: unknown) {
      error.value = extractApiError(err).message
    } finally {
      loading.value = false
    }
  }

  const updateProfile = (d: ProfileUpdatePayload) =>
    withSave(() => cvBuilderService.updateProfile(d))
  const updateSkills = (s: string[]) => withSave(() => cvBuilderService.updateSkills(s))
  const uploadPhoto = (file: File) => withSave(() => cvBuilderService.uploadPhoto(file))
  const deletePhoto = () => withSave(() => cvBuilderService.deletePhoto())

  // Work Experiences
  const createWorkExperience = (d: WorkExperiencePayload) =>
    withSave(() => cvBuilderService.createWorkExperience(d))
  const updateWorkExperience = (id: string, d: WorkExperiencePayload) =>
    withSave(() => cvBuilderService.updateWorkExperience(id, d))
  const deleteWorkExperience = (id: string) =>
    withSave(() => cvBuilderService.deleteWorkExperience(id))

  // Educations
  const createEducation = (d: EducationPayload) =>
    withSave(() => cvBuilderService.createEducation(d))
  const updateEducation = (id: string, d: EducationPayload) =>
    withSave(() => cvBuilderService.updateEducation(id, d))
  const deleteEducation = (id: string) => withSave(() => cvBuilderService.deleteEducation(id))

  // Languages
  const createLanguage = (d: LanguagePayload) => withSave(() => cvBuilderService.createLanguage(d))
  const updateLanguage = (id: string, d: LanguagePayload) =>
    withSave(() => cvBuilderService.updateLanguage(id, d))
  const deleteLanguage = (id: string) => withSave(() => cvBuilderService.deleteLanguage(id))

  // Certifications
  const createCertification = (d: CertificationPayload) =>
    withSave(() => cvBuilderService.createCertification(d))
  const updateCertification = (id: string, d: CertificationPayload) =>
    withSave(() => cvBuilderService.updateCertification(id, d))
  const deleteCertification = (id: string) =>
    withSave(() => cvBuilderService.deleteCertification(id))

  return {
    profile,
    loading,
    saving,
    error,
    fieldErrors,
    clearErrors,
    fetchProfile,
    updateProfile,
    updateSkills,
    uploadPhoto,
    deletePhoto,
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
  }
})
