import * as yup from 'yup'
import type { Composer } from 'vue-i18n'

export function createEducationSchema(t: Composer['t']) {
  return yup.object({
    institution: yup.string().required(t('validation.required')).max(255, t('validation.maxLength', { max: 255 })),
    degree: yup.string().max(255, t('validation.maxLength', { max: 255 })),
    educationLevel: yup.string(),
    fieldOfStudy: yup.string().max(255, t('validation.maxLength', { max: 255 })),
    startDate: yup.string(),
    endDate: yup.string().nullable(),
    description: yup.string(),
  })
}
