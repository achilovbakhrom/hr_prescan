import { ref } from 'vue'
import { defineStore } from 'pinia'
import { extractApiError, type FieldErrors } from '@/shared/api/errors'
import { vacancyService } from '../services/vacancy.service'
import { useVacancyItems } from './useVacancyItems'
import type { Vacancy, VacancyDetail, VacancyStatus, CreateVacancyRequest, UpdateVacancyRequest } from '../types/vacancy.types'

export const useVacancyStore = defineStore('vacancy', () => {
  const vacancies = ref<Vacancy[]>([])
  const currentVacancy = ref<VacancyDetail | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const fieldErrors = ref<FieldErrors>({})

  function clearErrors(): void { error.value = null; fieldErrors.value = {} }

  function handleError(err: unknown): never {
    const apiError = extractApiError(err)
    error.value = apiError.message
    if ('fieldErrors' in apiError) fieldErrors.value = (apiError as { fieldErrors: FieldErrors }).fieldErrors
    throw apiError
  }

  const { addCriteria, updateCriteria, deleteCriteria, addQuestion, updateQuestion, deleteQuestion } =
    useVacancyItems(currentVacancy, handleError)

  async function fetchVacancies(params?: { status?: string }): Promise<void> {
    loading.value = true; clearErrors()
    try { vacancies.value = await vacancyService.list(params) }
    catch (err: unknown) { error.value = extractApiError(err).message }
    finally { loading.value = false }
  }

  async function createVacancy(data: CreateVacancyRequest): Promise<Vacancy> {
    loading.value = true; clearErrors()
    try { const vacancy = await vacancyService.create(data); vacancies.value.unshift(vacancy); return vacancy }
    catch (err: unknown) { loading.value = false; handleError(err) }
    finally { loading.value = false }
  }

  async function deleteVacancy(id: string): Promise<void> {
    try { await vacancyService.deleteVacancy(id); vacancies.value = vacancies.value.filter(v => v.id !== id) }
    catch (err: unknown) { handleError(err) }
  }

  async function fetchVacancyDetail(id: string): Promise<void> {
    loading.value = true; clearErrors()
    try { currentVacancy.value = await vacancyService.getDetail(id) }
    catch (err: unknown) { error.value = extractApiError(err).message }
    finally { loading.value = false }
  }

  async function updateVacancy(id: string, data: UpdateVacancyRequest): Promise<void> {
    loading.value = true; clearErrors()
    try {
      const updated = await vacancyService.update(id, data)
      if (currentVacancy.value?.id === id) Object.assign(currentVacancy.value, updated)
      const index = vacancies.value.findIndex((v) => v.id === id)
      if (index !== -1) vacancies.value[index] = updated
    } catch (err: unknown) { loading.value = false; handleError(err) }
    finally { loading.value = false }
  }

  async function changeStatus(id: string, status: VacancyStatus): Promise<void> {
    loading.value = true; error.value = null
    try {
      const updated = await vacancyService.updateStatus(id, status)
      if (currentVacancy.value?.id === id) currentVacancy.value.status = updated.status
      const index = vacancies.value.findIndex((v) => v.id === id)
      if (index !== -1) vacancies.value[index] = updated
    } catch (err: unknown) { handleError(err) }
    finally { loading.value = false }
  }

  async function generateQuestions(vacancyId: string): Promise<void> {
    loading.value = true; error.value = null
    try {
      const questions = await vacancyService.generateQuestions(vacancyId)
      if (currentVacancy.value?.id === vacancyId) {
        currentVacancy.value.questions.push(...questions)
        currentVacancy.value.questionsCount += questions.length
      }
    } catch (err: unknown) { handleError(err) }
    finally { loading.value = false }
  }

  return {
    vacancies, currentVacancy, loading, error, fieldErrors,
    clearErrors, fetchVacancies, createVacancy, deleteVacancy, fetchVacancyDetail,
    updateVacancy, changeStatus,
    addCriteria, updateCriteria, deleteCriteria,
    addQuestion, updateQuestion, deleteQuestion, generateQuestions,
  }
})
