import { defineStore } from 'pinia'
import { useCvBuilderProfileStore } from './cv-builder-profile.store'
import { useCvBuilderCvStore } from './cv-builder-cv.store'
import { computed } from 'vue'
import type {
  ProfileUpdatePayload,
  WorkExperiencePayload,
  EducationPayload,
  LanguagePayload,
  CertificationPayload,
  CvChatMessage,
} from '../types/cv-builder.types'

/**
 * Facade store that delegates to profile and CV sub-stores.
 * Keeps the public API identical so existing consumers don't break.
 */
export const useCvBuilderStore = defineStore('cvBuilder', () => {
  const profileStore = useCvBuilderProfileStore()
  const cvStore = useCvBuilderCvStore()

  // Unified reactive state
  const profile = computed({
    get: () => profileStore.profile,
    set: (v) => {
      profileStore.profile = v
    },
  })
  const loading = computed(() => profileStore.loading)
  const saving = computed(() => profileStore.saving)
  const parsing = computed(() => cvStore.parsing)
  const generating = computed(() => cvStore.generating)
  const improving = computed(() => cvStore.improving)
  const error = computed(() => profileStore.error || cvStore.error)
  const fieldErrors = computed(() => ({
    ...profileStore.fieldErrors,
    ...cvStore.fieldErrors,
  }))

  function clearErrors(): void {
    profileStore.clearErrors()
    cvStore.clearErrors()
  }

  // Delegate to profile store
  const fetchProfile = profileStore.fetchProfile.bind(profileStore)
  const updateProfile = (d: ProfileUpdatePayload) => profileStore.updateProfile(d)
  const updateSkills = (s: string[]) => profileStore.updateSkills(s)
  const createWorkExperience = (d: WorkExperiencePayload) => profileStore.createWorkExperience(d)
  const updateWorkExperience = (id: string, d: WorkExperiencePayload) =>
    profileStore.updateWorkExperience(id, d)
  const deleteWorkExperience = (id: string) => profileStore.deleteWorkExperience(id)
  const createEducation = (d: EducationPayload) => profileStore.createEducation(d)
  const updateEducation = (id: string, d: EducationPayload) => profileStore.updateEducation(id, d)
  const deleteEducation = (id: string) => profileStore.deleteEducation(id)
  const createLanguage = (d: LanguagePayload) => profileStore.createLanguage(d)
  const updateLanguage = (id: string, d: LanguagePayload) => profileStore.updateLanguage(id, d)
  const deleteLanguage = (id: string) => profileStore.deleteLanguage(id)
  const createCertification = (d: CertificationPayload) => profileStore.createCertification(d)
  const updateCertification = (id: string, d: CertificationPayload) =>
    profileStore.updateCertification(id, d)
  const deleteCertification = (id: string) => profileStore.deleteCertification(id)

  // Delegate to CV store
  const generatePdf = cvStore.generatePdf.bind(cvStore)
  const parseCv = cvStore.parseCv.bind(cvStore)
  const improveCvSection = cvStore.improveCvSection.bind(cvStore)
  const cvAiChat = (m: CvChatMessage[]) => cvStore.cvAiChat(m)
  const cvAiGenerate = (m: CvChatMessage[]) => cvStore.cvAiGenerate(m)

  return {
    profile,
    loading,
    saving,
    parsing,
    generating,
    improving,
    error,
    fieldErrors,
    clearErrors,
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
    cvAiChat,
    cvAiGenerate,
  }
})
