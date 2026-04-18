import { ref } from 'vue'
import { defineStore } from 'pinia'
import { extractApiError, type FieldErrors } from '@/shared/api/errors'
import { cvBuilderService } from '../services/cv-builder.service'
import { useCvBuilderProfileStore } from './cv-builder-profile.store'
import type { CvGenerateResult } from '../types/cv-builder.types'

export const useCvBuilderCvStore = defineStore('cvBuilderCv', () => {
  const parsing = ref(false)
  const generating = ref(false)
  const improving = ref(false)
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

  // CV PDF Generation
  async function generatePdf(template: string, name?: string): Promise<CvGenerateResult> {
    const profileStore = useCvBuilderProfileStore()
    generating.value = true
    clearErrors()
    try {
      const result = await cvBuilderService.generatePdf(template, name)
      await profileStore.fetchProfile()
      return result
    } catch (err: unknown) {
      generating.value = false
      handleError(err)
    } finally {
      generating.value = false
    }
  }

  // CV Parsing (AI)
  async function parseCv(file: File): Promise<void> {
    const profileStore = useCvBuilderProfileStore()
    parsing.value = true
    clearErrors()
    try {
      profileStore.profile = await cvBuilderService.parseCv(file)
    } catch (err: unknown) {
      parsing.value = false
      handleError(err)
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
    clearErrors()
    try {
      const improved = await cvBuilderService.improveCvSection(section, content, jobTitle)
      return improved
    } catch (err: unknown) {
      improving.value = false
      handleError(err)
    } finally {
      improving.value = false
    }
  }

  return {
    parsing,
    generating,
    improving,
    error,
    fieldErrors,
    clearErrors,
    generatePdf,
    parseCv,
    improveCvSection,
  }
})
