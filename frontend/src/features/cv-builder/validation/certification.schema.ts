import * as yup from 'yup'
import type { Composer } from 'vue-i18n'

export function createCertificationSchema(t: Composer['t']) {
  return yup.object({
    name: yup
      .string()
      .required(t('validation.required'))
      .max(255, t('validation.maxLength', { max: 255 })),
    issuingOrganization: yup.string().max(255, t('validation.maxLength', { max: 255 })),
    issueDate: yup.string().nullable(),
    expiryDate: yup.string().nullable(),
    credentialUrl: yup.string().url(t('validation.invalidUrl')),
  })
}
