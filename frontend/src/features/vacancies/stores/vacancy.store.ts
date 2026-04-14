import { ref } from 'vue'
import { defineStore } from 'pinia'
import { extractErrorMessage } from '@/shared/api/errors'
import { vacancyService } from '../services/vacancy.service'
import type {
  Vacancy,
  VacancyDetail,
  VacancyStatus,
  VacancyCriteria,
  InterviewQuestion,
  CreateVacancyRequest,
  UpdateVacancyRequest,
} from '../types/vacancy.types'

export const useVacancyStore = defineStore('vacancy', () => {
  const vacancies = ref<Vacancy[]>([])
  const currentVacancy = ref<VacancyDetail | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchVacancies(params?: {
    status?: string
  }): Promise<void> {
    loading.value = true
    error.value = null
    try {
      vacancies.value = await vacancyService.list(params)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function createVacancy(data: CreateVacancyRequest): Promise<Vacancy> {
    loading.value = true
    error.value = null
    try {
      const vacancy = await vacancyService.create(data)
      vacancies.value.unshift(vacancy)
      return vacancy
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function deleteVacancy(id: string): Promise<void> {
    try {
      await vacancyService.deleteVacancy(id)
      vacancies.value = vacancies.value.filter(v => v.id !== id)
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    }
  }

  async function fetchVacancyDetail(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentVacancy.value = await vacancyService.getDetail(id)
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function updateVacancy(
    id: string,
    data: UpdateVacancyRequest,
  ): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const updated = await vacancyService.update(id, data)
      if (currentVacancy.value?.id === id) {
        Object.assign(currentVacancy.value, updated)
      }
      const index = vacancies.value.findIndex((v) => v.id === id)
      if (index !== -1) {
        vacancies.value[index] = updated
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function changeStatus(
    id: string,
    status: VacancyStatus,
  ): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const updated = await vacancyService.updateStatus(id, status)
      if (currentVacancy.value?.id === id) {
        currentVacancy.value.status = updated.status
      }
      const index = vacancies.value.findIndex((v) => v.id === id)
      if (index !== -1) {
        vacancies.value[index] = updated
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function addCriteria(
    vacancyId: string,
    data: { name: string; description?: string; weight?: number; step?: string },
  ): Promise<void> {
    try {
      const criteria = await vacancyService.addCriteria(vacancyId, data)
      if (currentVacancy.value?.id === vacancyId) {
        currentVacancy.value.criteria.push(criteria)
        currentVacancy.value.criteriaCount += 1
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    }
  }

  async function updateCriteria(
    vacancyId: string,
    criteriaId: string,
    data: Partial<VacancyCriteria>,
  ): Promise<void> {
    try {
      const updated = await vacancyService.updateCriteria(
        vacancyId,
        criteriaId,
        data,
      )
      if (currentVacancy.value?.id === vacancyId) {
        const index = currentVacancy.value.criteria.findIndex(
          (c) => c.id === criteriaId,
        )
        if (index !== -1) {
          currentVacancy.value.criteria[index] = updated
        }
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    }
  }

  async function deleteCriteria(
    vacancyId: string,
    criteriaId: string,
  ): Promise<void> {
    try {
      await vacancyService.deleteCriteria(vacancyId, criteriaId)
      if (currentVacancy.value?.id === vacancyId) {
        currentVacancy.value.criteria =
          currentVacancy.value.criteria.filter((c) => c.id !== criteriaId)
        currentVacancy.value.criteriaCount -= 1
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    }
  }

  async function addQuestion(
    vacancyId: string,
    data: { text: string; category?: string; step?: string },
  ): Promise<void> {
    try {
      const question = await vacancyService.addQuestion(vacancyId, data)
      if (currentVacancy.value?.id === vacancyId) {
        currentVacancy.value.questions.push(question)
        currentVacancy.value.questionsCount += 1
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    }
  }

  async function updateQuestion(
    vacancyId: string,
    questionId: string,
    data: Partial<InterviewQuestion>,
  ): Promise<void> {
    try {
      const updated = await vacancyService.updateQuestion(
        vacancyId,
        questionId,
        data,
      )
      if (currentVacancy.value?.id === vacancyId) {
        const index = currentVacancy.value.questions.findIndex(
          (q) => q.id === questionId,
        )
        if (index !== -1) {
          currentVacancy.value.questions[index] = updated
        }
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    }
  }

  async function deleteQuestion(
    vacancyId: string,
    questionId: string,
  ): Promise<void> {
    try {
      await vacancyService.deleteQuestion(vacancyId, questionId)
      if (currentVacancy.value?.id === vacancyId) {
        currentVacancy.value.questions =
          currentVacancy.value.questions.filter((q) => q.id !== questionId)
        currentVacancy.value.questionsCount -= 1
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    }
  }

  async function generateQuestions(vacancyId: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const questions = await vacancyService.generateQuestions(vacancyId)
      if (currentVacancy.value?.id === vacancyId) {
        currentVacancy.value.questions.push(...questions)
        currentVacancy.value.questionsCount += questions.length
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  return {
    vacancies,
    currentVacancy,
    loading,
    error,
    fetchVacancies,
    createVacancy,
    deleteVacancy,
    fetchVacancyDetail,
    updateVacancy,
    changeStatus,
    addCriteria,
    updateCriteria,
    deleteCriteria,
    addQuestion,
    updateQuestion,
    deleteQuestion,
    generateQuestions,
  }
})
