export const getEmploymentOptions = (t: (key: string) => string) => [
  { label: t('vacancies.employment.fullTime'), value: 'full_time' },
  { label: t('vacancies.employment.partTime'), value: 'part_time' },
  { label: t('vacancies.employment.contract'), value: 'contract' },
  { label: t('vacancies.employment.internship'), value: 'internship' },
]

export const getExperienceOptions = (t: (key: string) => string) => [
  { label: t('vacancies.experience.junior'), value: 'junior' },
  { label: t('vacancies.experience.middle'), value: 'middle' },
  { label: t('vacancies.experience.senior'), value: 'senior' },
  { label: t('vacancies.experience.lead'), value: 'lead' },
  { label: t('vacancies.experience.director'), value: 'director' },
]

export const CURRENCY_OPTIONS = [
  { label: 'USD', value: 'USD' },
  { label: 'EUR', value: 'EUR' },
  { label: 'GBP', value: 'GBP' },
  { label: 'UZS', value: 'UZS' },
]

export const getVisibilityOptions = (t: (key: string) => string) => [
  { label: t('vacancies.visibility.public'), value: 'public' },
  { label: t('vacancies.visibility.private'), value: 'private' },
]

export const getInterviewModeOptions = (t: (key: string) => string) => [
  { label: t('vacancies.interviewMode.chat'), value: 'chat' },
  { label: t('vacancies.interviewMode.meet'), value: 'meet' },
]
