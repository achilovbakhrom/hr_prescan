import { isAxiosError } from 'axios'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from 'primevue/usetoast'
import { vacancyService } from '../services/vacancy.service'
import type { VacancyGenerationContext } from '../types/vacancy.types'
import type { useVacancyForm } from './useVacancyForm'

type VacancyFormState = ReturnType<typeof useVacancyForm>

export function useVacancyContentGeneration(form: VacancyFormState) {
  const { t } = useI18n()
  const toast = useToast()
  const visible = ref(false)
  const generating = ref(false)
  const instruction = ref('')
  const context = ref<VacancyGenerationContext | null>(null)
  const canGenerate = computed(() => form.title.value.trim().length >= 5)
  const hasContext = computed(() => Boolean(context.value?.turns.length))

  function errorMessage(error: unknown): string {
    if (isAxiosError<{ detail?: string }>(error)) {
      return error.response?.data?.detail || t('vacancies.form.generateWithAIError')
    }
    return t('vacancies.form.generateWithAIError')
  }

  async function generate(): Promise<void> {
    if (!canGenerate.value || generating.value) return
    generating.value = true
    try {
      const content = await vacancyService.generateContent({
        title: form.title.value.trim(),
        description: form.description.value,
        requirements: form.requirements.value,
        responsibilities: form.responsibilities.value,
        skills: form.skills.value,
        salaryMin: form.salaryMin.value,
        salaryMax: form.salaryMax.value,
        salaryCurrency: form.salaryCurrency.value,
        location: form.location.value || undefined,
        isRemote: form.isRemote.value,
        employmentType: form.employmentType.value,
        experienceLevel: form.experienceLevel.value,
        additionalInstruction: instruction.value.trim(),
        generationContext: context.value || undefined,
      })
      if (content.description) form.description.value = content.description
      if (content.requirements) form.requirements.value = content.requirements
      if (content.responsibilities) form.responsibilities.value = content.responsibilities
      if (content.generationContext) context.value = content.generationContext
      if (!content.description && !content.requirements && !content.responsibilities) {
        throw new Error(t('vacancies.form.generateWithAIError'))
      }
      toast.add({
        severity: 'success',
        summary: t('vacancies.form.generateWithAISuccess'),
        life: 2500,
      })
      visible.value = false
    } catch (error) {
      toast.add({
        severity: 'error',
        summary: t('vacancies.form.generateWithAIError'),
        detail: errorMessage(error),
        life: 4000,
      })
    } finally {
      generating.value = false
    }
  }

  return { canGenerate, context, generate, generating, hasContext, instruction, visible }
}
