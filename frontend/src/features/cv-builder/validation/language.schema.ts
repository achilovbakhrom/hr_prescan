import * as yup from 'yup'
import type { Composer } from 'vue-i18n'

export function createLanguageSchema(t: Composer['t']) {
  return yup.object({
    language: yup.string().required(t('validation.required')),
    proficiency: yup.string().required(t('validation.required')),
  })
}
