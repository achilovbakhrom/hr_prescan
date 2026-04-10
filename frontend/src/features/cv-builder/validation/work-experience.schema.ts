import * as yup from 'yup'
import type { Composer } from 'vue-i18n'

export function createWorkExperienceSchema(t: Composer['t']) {
  return yup.object({
    companyName: yup.string().required(t('validation.required')).max(255, t('validation.maxLength', { max: 255 })),
    position: yup.string().required(t('validation.required')).max(255, t('validation.maxLength', { max: 255 })),
    employmentType: yup.string(),
    location: yup.string().max(255, t('validation.maxLength', { max: 255 })),
    startDate: yup.string().required(t('validation.required')),
    endDate: yup.string().nullable(),
    isCurrent: yup.boolean(),
    description: yup.string(),
  })
}
