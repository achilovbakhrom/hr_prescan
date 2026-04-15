import * as yup from 'yup'
import type { Composer } from 'vue-i18n'

export function createPersonalInfoSchema(t: Composer['t']) {
  return yup.object({
    headline: yup.string().required(t('validation.required')).max(255, t('validation.maxLength', { max: 255 })),
    summary: yup.string().required(t('validation.required')),
    location: yup.string().max(255, t('validation.maxLength', { max: 255 })),
    linkedinUrl: yup.string().url(t('validation.invalidUrl')),
    githubUrl: yup.string().url(t('validation.invalidUrl')),
    websiteUrl: yup.string().url(t('validation.invalidUrl')),
    desiredSalaryNegotiable: yup.boolean(),
    desiredSalaryMin: yup
      .number()
      .nullable()
      .transform((v, orig) => (orig === '' || orig === null ? null : v))
      .min(0, t('validation.positiveNumber'))
      .when('desiredSalaryNegotiable', {
        is: false,
        then: (s) => s.required(t('validation.required')),
      }),
    desiredSalaryMax: yup
      .number()
      .nullable()
      .transform((v, orig) => (orig === '' || orig === null ? null : v))
      .min(0, t('validation.positiveNumber'))
      .when('desiredSalaryNegotiable', {
        is: false,
        then: (s) => s.required(t('validation.required'))
          .test('salary-range', t('validation.salaryRange'), function (max) {
            const min = this.parent.desiredSalaryMin
            if (min == null || max == null) return true
            return max >= min
          }),
      }),
    desiredEmploymentType: yup.string().required(t('validation.required')),
  })
}
