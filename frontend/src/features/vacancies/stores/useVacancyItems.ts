import type { Ref } from 'vue'
import { vacancyService } from '../services/vacancy.service'
import type { VacancyDetail, VacancyCriteria, InterviewQuestion } from '../types/vacancy.types'

export function useVacancyItems(
  currentVacancy: Ref<VacancyDetail | null>,
  handleError: (err: unknown) => never,
) {
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
    } catch (err: unknown) { handleError(err) }
  }

  async function updateCriteria(vacancyId: string, criteriaId: string, data: Partial<VacancyCriteria>): Promise<void> {
    try {
      const updated = await vacancyService.updateCriteria(vacancyId, criteriaId, data)
      if (currentVacancy.value?.id === vacancyId) {
        const index = currentVacancy.value.criteria.findIndex((c) => c.id === criteriaId)
        if (index !== -1) currentVacancy.value.criteria[index] = updated
      }
    } catch (err: unknown) { handleError(err) }
  }

  async function deleteCriteria(vacancyId: string, criteriaId: string): Promise<void> {
    try {
      await vacancyService.deleteCriteria(vacancyId, criteriaId)
      if (currentVacancy.value?.id === vacancyId) {
        currentVacancy.value.criteria = currentVacancy.value.criteria.filter((c) => c.id !== criteriaId)
        currentVacancy.value.criteriaCount -= 1
      }
    } catch (err: unknown) { handleError(err) }
  }

  async function addQuestion(vacancyId: string, data: { text: string; category?: string; step?: string }): Promise<void> {
    try {
      const question = await vacancyService.addQuestion(vacancyId, data)
      if (currentVacancy.value?.id === vacancyId) {
        currentVacancy.value.questions.push(question)
        currentVacancy.value.questionsCount += 1
      }
    } catch (err: unknown) { handleError(err) }
  }

  async function updateQuestion(vacancyId: string, questionId: string, data: Partial<InterviewQuestion>): Promise<void> {
    try {
      const updated = await vacancyService.updateQuestion(vacancyId, questionId, data)
      if (currentVacancy.value?.id === vacancyId) {
        const index = currentVacancy.value.questions.findIndex((q) => q.id === questionId)
        if (index !== -1) currentVacancy.value.questions[index] = updated
      }
    } catch (err: unknown) { handleError(err) }
  }

  async function deleteQuestion(vacancyId: string, questionId: string): Promise<void> {
    try {
      await vacancyService.deleteQuestion(vacancyId, questionId)
      if (currentVacancy.value?.id === vacancyId) {
        currentVacancy.value.questions = currentVacancy.value.questions.filter((q) => q.id !== questionId)
        currentVacancy.value.questionsCount -= 1
      }
    } catch (err: unknown) { handleError(err) }
  }

  return { addCriteria, updateCriteria, deleteCriteria, addQuestion, updateQuestion, deleteQuestion }
}
