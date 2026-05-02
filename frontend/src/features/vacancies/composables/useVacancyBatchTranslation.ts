import type { ComputedRef, Ref } from 'vue'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from 'primevue/usetoast'
import { batchTranslateItems } from '@/shared/api/translate'
import { getApiErrorMessage } from '@/shared/api/errors'
import { getLocale } from '@/shared/i18n'
import type { VacancyDetail } from '../types/vacancy.types'

type ItemType = 'criteria' | 'questions'
type Step = 'prescanning' | 'interview'
type TranslationKey = `${Step}:${ItemType}`

export function useVacancyBatchTranslation(
  vacancyId: ComputedRef<string>,
  vacancy: ComputedRef<VacancyDetail | null>,
): {
  translatingKey: Ref<TranslationKey | null>
  handleBatchTranslate: (itemType: ItemType, step: Step) => Promise<void>
} {
  const { t } = useI18n()
  const toast = useToast()
  const translatingKey = ref<TranslationKey | null>(null)

  async function handleBatchTranslate(itemType: ItemType, step: Step): Promise<void> {
    if (translatingKey.value) return
    translatingKey.value = `${step}:${itemType}`
    try {
      const result = await batchTranslateItems({
        vacancyId: vacancyId.value,
        itemType,
        step,
        targetLanguage: getLocale(),
      })
      const currentVacancy = vacancy.value
      if (currentVacancy) {
        const itemList =
          itemType === 'criteria' ? currentVacancy.criteria : currentVacancy.questions
        for (const translated of result.items) {
          const item = itemList.find((i) => i.id === translated.id)
          if (item) item.translations = translated.translations
        }
      }
      toast.add({ severity: 'success', summary: t('common.saved'), life: 2500 })
    } catch (error) {
      toast.add({
        severity: 'error',
        summary: getApiErrorMessage(error, t('common.error')),
        life: 4500,
      })
    } finally {
      translatingKey.value = null
    }
  }

  return { translatingKey, handleBatchTranslate }
}
